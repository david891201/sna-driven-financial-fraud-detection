import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class FakeTeradataClient:
    def __init__(
        self,
        configs: dict,
        seed: int = 42,
        tx_start_date: str = "2024-01-01",       # 交易資料開始日
        alert_start_date: str = "2024-02-01"    # 警示註記開始日
    ):
        random.seed(seed)
        np.random.seed(seed)
        self.tx_start_date = datetime.strptime(tx_start_date, "%Y-%m-%d")
        self.alert_start_date = datetime.strptime(alert_start_date, "%Y-%m-%d")
        self.configs = configs

    def query(self, sql: str) -> pd.DataFrame:
        """
        模擬 Teradata 查詢結果：
        - 若 SQL 包含 'transaction'：回傳交易資料
        - 若 SQL 包含 'alert'：回傳警示帳戶資料
        """
        sql_lower = sql.lower()
        if "transaction" in sql_lower:
            return self._fake_transaction_data()
        elif "alert" in sql_lower:
            return self._fake_alert_data()
        else:
            raise ValueError("FakeTeradataClient: 無法識別 SQL 類型，請包含 'transaction' 或 'alert' 字樣")

    # ----------------------------
    # 生成第一種 DataFrame：交易資料
    # ----------------------------
    def _fake_transaction_data(self, days=5, tx_per_day=8):
        """
        生成交易資料：
        欄位：SYSTEM_DATE, SENDER_ACCOUNT_ID, RECEIVER_ACCOUNT_ID, TXN_AMT_ABS
        - 帳號之間有收付款關係
        - 為模擬真實情況，同一天可有多筆交易
        """
        accounts = [f"A{100+i}" for i in range(10)]  # 共 10 個帳戶
        rows = []
        for d in range(days):
            date = self.tx_start_date + timedelta(days=d)
            for _ in range(tx_per_day):
                src = random.choice(accounts)
                dst_candidates = [a for a in accounts if a != src]
                dst = random.choice(dst_candidates)
                amount = round(random.uniform(500, 50000), 2)
                rows.append({
                    self.configs.get("date_column_name"): date,
                    self.configs.get("sender_column_name"): src,
                    self.configs.get("receiver_column_name"): dst,
                    self.configs.get("raw_txn_amt_column_name"): amount
                })
        self._cached_transactions = pd.DataFrame(rows)
        self._cached_transactions[self.configs.get("date_column_name")] = pd.to_datetime(self._cached_transactions[self.configs.get("date_column_name")])
        return self._cached_transactions

    # ----------------------------
    # 生成第二種 DataFrame：被下警示註記的帳戶清單
    # ----------------------------
    def _fake_alert_data(self, alert_days: int=5):
        """
        欄位：ACCOUNT_ID, CREATE_DATE(註記日期), FLAG(註記類型）
        - 帳號從假交易資料的 SENDER_ACCOUNT_ID 挑選
        - 此為模擬情況，一個帳號僅一筆警示註記
        - 為模擬真實情況，註記日期採隨機分配
        """
        if not hasattr(self, "_cached_transactions"):
            raise RuntimeError("請先查詢一次 transaction 資料來產生帳號列表")
        src_accounts = list(self._cached_transactions[self.configs.get("sender_column_name")].unique())
        alert_accounts = random.sample(src_accounts, k=max(1, len(src_accounts)//3))
        rows = []
        for acct in alert_accounts:
            offset = random.randint(0, alert_days - 1)
            alert_date = self.alert_start_date + timedelta(days=offset)
            rows.append({
                self.configs.get("alert_account_column_name"): acct,
                self.configs.get("alert_date_column_name"): alert_date,
                self.configs.get("alert_flag_column_name"): "ALERT"
            })
        df_alert = pd.DataFrame(rows)
        df_alert[self.configs.get("alert_date_column_name")] = pd.to_datetime(df_alert[self.configs.get("alert_date_column_name")])
        # 將原 dataframe 轉換成 dict， key 爲日期，value 為於該日期被下警示註記的帳號 list
        date_account_dict = df_alert.groupby(self.configs.get("alert_date_column_name"))[self.configs.get("alert_account_column_name")].apply(list).to_dict()
        return date_account_dict

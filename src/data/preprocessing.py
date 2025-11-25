import pandas as pd
from datetime import timedelta

def process_transactions(data_raw: pd.DataFrame, date: pd.Timestamp, configs: dict) -> pd.DataFrame:
    """
    根據來源警示戶被下警示註記的日期，以此為基準所設定的日期範圍篩選交易資料，並依匯款人與收款人進行 groupby，
    產生彙總後的 dataframe。

    參數:
        data_raw: 原始交易數據，需包含日期、來源帳號、收款帳號、交易金額欄位
        date: 來源警示戶被下警示註記的日期
        configs: 從 conf/job.conf import的參數設定檔
    """

    date_col = configs["date_column_name"]
    sender_col = configs["sender_column_name"]
    receiver_col = configs["receiver_column_name"]
    raw_amt_col = configs["raw_txn_amt_column_name"]
    txn_amt_col = configs["txn_amt_column_name"]
    txn_cnt_col = configs["txn_cnt_column_name"]
    days = configs["txn_days"]

    # 計算日期區間
    start_date = date - timedelta(days=days)
    end_date = date

    # 取出基準日往前推 days 的所有交易，從取出的交易中，尋找警示戶的鄰居
    mask = (data_raw[date_col] >= start_date) & (data_raw[date_col] <= end_date)
    df = data_raw[mask]
    df = (
        df.groupby([sender_col, receiver_col])
        .agg(
            **{
                txn_amt_col: (raw_amt_col, "sum"),
                txn_cnt_col: (raw_amt_col, "size")
            }
        )
        .reset_index()
    )
    return df

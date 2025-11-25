# job.conf 各參數說明

## txn_days
- 用途：取基準日往前回推幾天內的交易資料
- 類型：int
- 預設值：60（也就是取基準值往前回推兩個月內的交易資料）

## radius
- 用途：尋找警示戶距離幾度以內的鄰居
- 類型：int
- 預設值：6

## txn_amt_column_name
- 用途：groupby 後的「交易金額」欄位名稱
- 類型：str
- 預設：AGG_TXN_AMT

## txn_cnt_column_name
- 用途：groupby 後的「交易次數」欄位名稱
- 類型：str
- 預設：AGG_TXN_CNT

## date_column_name
- 用途：database 「交易日期」欄位名稱
- 類型：str
- 預設：SYSTEM_DATE

## sender_column_name
- 用途：database 「匯款帳號」欄位名稱
- 類型：str
- 預設：SENDER_ACCOUNT_ID

## receiver_column_name
- 用途：database 「收款帳號」欄位名稱
- 類型：str
- 預設：RECEIVER_ACCOUNT_ID

## raw_txn_amt_column_name
- 用途：database 「交易金額」欄位名稱
- 類型：str
- 預設：TXN_AMT_ABS

## alert_date_column_name
- 用途：database 「註記日期」欄位名稱
- 類型：str
- 預設：CREATE_DATE

## alert_account_column_name
- 用途：database 「被下註記的帳號」欄位名稱
- 類型：str
- 預設：ACCOUNT_ID

## alert_flag_column_name
- 用途：database 「註記類型」欄位名稱
- 類型：str
- 預設：FLAG


import pandas as pd

def add_neighbor_counts(df: pd.DataFrame) -> pd.DataFrame:
    """
    計算每個帳戶同時為幾個警示戶的鄰居。
    """
    neighbor_counts = df["帳號"].value_counts()
    df["該帳戶同時為幾個警示戶的鄰居"] = df["帳號"].map(neighbor_counts)
    return df
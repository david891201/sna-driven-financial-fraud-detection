import networkx as nx
import pandas as pd
from typing import List, Optional, Union

def build_graph(df: pd.DataFrame, configs: dict) -> nx.Graph:
    """
    利用 aggregate 後的交易資料建立關聯網絡圖

    參數：
        df: aggregate 後的交易資料
        configs: 從 conf/job.conf import的參數設定檔
    """
    G = nx.from_pandas_edgelist(
        df,
        source=configs.get("sender_column_name"),
        target=configs.get("receiver_column_name"),
        edge_attr=[configs.get("txn_amt_column_name"), configs.get("txn_cnt_column_name")],
        create_using=nx.DiGraph(),
    )
    return G

def build_ego_graph(G: nx.DiGraph, source_node: str, configs: dict):
    """
    建立以 source_node-也就是來源警示戶，為中心點的關聯網絡圖，藉此找到 source_node 的鄰居

    參數：
        G: 完整的關聯網絡圖
        source_node: 來源警示戶的帳號
        radius: 尋找距離幾度以內的鄰居，數字越大代表鄰居納入的範圍越廣
    """
    subgraph = nx.ego_graph(G, source_node, radius=configs.get('radius'))
    return subgraph

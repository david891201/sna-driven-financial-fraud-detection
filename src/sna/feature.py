import networkx as nx
import pandas as pd

def _sum_in_edges(G: nx.DiGraph, node: str, attr: str) -> float:
    """計算匯入 node 的總金流或總次數"""
    return sum(
        (G.get_edge_data(pred, node) or {}).get(attr, 0)
        for pred in G.predecessors(node)
    )

def _sum_out_edges(G: nx.DiGraph, node: str, attr: str):
    """計算從 node 匯出的總金流或總次數"""
    return sum(
        (G.get_edge_data(node, succ) or {}).get(attr, 0)
        for succ in G.successors(node)
    )

def _direct_edge_attr(G: nx.DiGraph, source_node: str, node: str, attr: str):
    """計算匯入 node 的警示戶直接金流（只有 source_node -也就是警示戶，的一度鄰居，才會有從警示戶匯入的直接金流）"""
    return (G.get_edge_data(source_node, node) or {}).get(attr, 0)

def _retrieve_source_features(G: nx.DiGraph, source_node: str, date: pd.Timestamp, configs: dict) -> dict[str, float | int]:
    """匯出來源節點-也就是警示戶，的相關特徵"""
    return {
        "來源節點帳號": source_node,
        "來源節點被下警示戶註記的日期": date,
        "來源節點的出度": G.out_degree(source_node),
        "匯入來源節點的總關聯金流": _sum_in_edges(G, source_node, configs.get("txn_amt_column_name")),
        "匯入來源節點的總次數": _sum_in_edges(G, source_node, configs.get("txn_cnt_column_name")),
        "從來源節點匯出的總關聯金流": _sum_out_edges(G, source_node, configs.get("txn_amt_column_name")),
        "從來源節點匯出的總次數": _sum_out_edges(G, source_node, configs.get("txn_cnt_column_name")),
    }

def _retrieve_node_features(G: nx.DiGraph, subgraph: nx.DiGraph, distances: dict, source_node: str, node: str, configs: dict) -> dict:
    """
    匯出 node-也就是警示戶的鄰居，的相關特徵

    參數：
        G: 完整的關聯網絡圖
        subgraph: 以某來源警示戶(source_node)為中心的關聯網絡圖
        distances: 儲存每個鄰居到來源警示帳戶的最短距離的dict，key為鄰居的帳號，value為該鄰居到來源警示戶的最短距離
        source_node: 來源警示戶的帳號
        node: 警示戶鄰居的帳號
        configs: 從 conf/job.conf 載入的參數 dict，要從裡面取出金流和交易次數的欄位名稱
    """
    direct_amt = _direct_edge_attr(subgraph, source_node, node, configs.get("txn_amt_column_name"))
    direct_cnt = _direct_edge_attr(subgraph, source_node, node, configs.get("txn_cnt_column_name"))
    total_in_amt = _sum_in_edges(G, node, configs.get("txn_amt_column_name"))
    total_in_cnt = _sum_in_edges(G, node, configs.get("txn_cnt_column_name"))
    return {
        "帳號": node,
        "鄰居度數": distances.get(node, 0),
        "匯入該帳戶的總關聯金流": total_in_amt,
        "匯入該帳戶的警示戶直接金流": direct_amt,
        "匯入該帳戶的警示戶間接金流": total_in_amt - direct_amt,
        "匯入該帳戶的總次數": total_in_cnt,
        "匯入該帳戶的警示戶直接次數": direct_cnt,
        "匯入該帳戶的警示戶間接次數": total_in_cnt - direct_cnt,
        "從該帳戶匯出的總關聯金流": _sum_out_edges(G, node, configs.get("txn_amt_column_name")),
        "從該帳戶匯出的總次數": _sum_out_edges(G, node, configs.get("txn_cnt_column_name")),
        "該帳戶的出入度": G.degree(node),
        "該帳戶的出度": G.out_degree(node),
        "該帳戶的入度": G.in_degree(node),
    }

def export_allnodes_features(G: nx.DiGraph, subgraph: nx.DiGraph, distances: dict, source_node: str, date: pd.Timestamp, configs: dict) -> pd.DataFrame:
    """
    批次匯出 node-警示戶鄰居的總特徵（總特徵 = node 自己的特徵 + 來源警示戶的特徵，一筆樣本的特徵就是由總特徵構成）
    """
    warning_feature = _retrieve_source_features(G, source_node, date, configs)  
    node_features = []
    for node in distances.keys():
        node_feature = _retrieve_node_features(G, subgraph, distances, source_node, node, configs)
        combined_feature = {**node_feature, **warning_feature}
        node_features.append(combined_feature)
    df = pd.DataFrame(node_features)
    return df
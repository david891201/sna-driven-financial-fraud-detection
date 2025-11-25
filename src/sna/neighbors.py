import networkx as nx

def generate_neighbor_information(subgraph: nx.DiGraph, source_node: str):
    """
    回傳每個鄰居到來源警示戶的最短距離 dict。

    參數：
        subgraph: 以 source_node-也就是來源警示戶，為中心點的關聯網絡圖
        source_node: 來源警示戶的帳號
    """
    path_lengths = nx.shortest_path_length(subgraph, source=source_node)
    distances = {
        node: dist
        for node, dist in path_lengths.items()
        if node != source_node
    }
    return distances
from tqdm.auto import tqdm
import pandas as pd

from src.db.fake_teradata_client import FakeTeradataClient
from src.data.preprocessing import process_transactions
from src.sna.graph import build_graph, build_ego_graph 
from src.sna.feature import export_allnodes_features
from src.sna.neighbors import generate_neighbor_information
from src.sna.postprocess import add_neighbor_counts

def run_pipeline(date: str, configs: dict):
    """
    Main Pipeline:
    1. 載入交易資料和警示帳戶註記資料
    2. 以日為單位，建立關聯網絡圖
    3. 以各警示帳號為單位，尋找該警示帳號的鄰居
    4. 提取各鄰居的特徵，以建立樣本
    5. 將所有警示戶的鄰居樣本彙整在同一個 dataframe，並提取額外新特徵
    """
    # --- 1. Load data ---------------------------------------------------------
    db = FakeTeradataClient(configs, alert_start_date=date)
    df_tx = db.query("SELECT * FROM transaction_table")
    alert_data = db.query("SELECT * FROM alert_table")
    # --- 2. Loop through alert dates -----------------------------------------
    df_list = []

    for date, acc in alert_data.items():
        agg_df_tx = process_transactions(df_tx, date, configs)
        G = build_graph(agg_df_tx, configs)

        # 僅保留於期間內有匯出紀錄的警示戶；無匯出者無出度鄰居可分析。
        target_accounts_id = [
            account for account in acc 
            if account in agg_df_tx[configs.get("sender_column_name")].values
        ] 

        # --- 3. Loop through each alert account to find neighbors -------------------------------
        for account_id in tqdm(target_accounts_id, desc=f"Processing {date}", colour="green"): 
            subgraph = build_ego_graph(G, account_id, configs)
            distances = generate_neighbor_information(subgraph, account_id)
            node_features = export_allnodes_features(
                G, subgraph, distances, account_id, date, configs
            )
            df_list.append(node_features)
        
    # --- 4. 將每個警示戶的鄰居樣本彙整在同一個dataframe，並提取額外新特徵 -------------------------------
    result_df = pd.concat(df_list, ignore_index=True) 
    result_df = add_neighbor_counts(result_df)
    
    return result_df

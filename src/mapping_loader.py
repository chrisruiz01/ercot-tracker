import pandas as pd

def load_settlement_point_mapping(filepath: str) -> pd.DataFrame:
    """
    Loads and processes ERCOT settlement point mapping file. 
    Returns a DataFrame with columns: settlement_point, settlement_point_type
    """
    mapping = pd.read_csv(filepath)
    mapping.columns = mapping.columns.str.strip().str.lower()

    def classify_type(row):
        if pd.notna(row.get("resource_node")):
            return "Resource Node"
        elif pd.notna(row.get("hub")):
            return "Hub"
        elif pd.notna(row.get("settlement_load_zone")):
            return "Load Zone"
        else:
            return "Unknown"
        
    mapping["settlement_point_type"] = mapping.apply(classify_type, axis=1)

    def get_settlement_point(row):
        if row["settlement_point_type"] == "Resource Node":
            return row["resource_node"]
        elif row["settlement_point_type"] == "Hub":
            return row["hub"]
        elif row["settlement_point_type"] == "Load Zone":
            return row["settlement_load_zone"]
        else:
            None 

    mapping["settlement_point"] = mapping.apply(get_settlement_point, axis=1)

    return mapping[["settlement_point", "settlement_point_type"]].dropna().drop_duplicates()
        
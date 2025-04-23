import os
import glob
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("POSTGRES_URI")
engine = create_engine(db_url)

# Loop through all cleaned daily CSVs
raw_dir = "data/raw"
csv_files = glob.glob(os.path.join(raw_dir, "*_da_spp.csv"))

with engine.begin() as conn:  # ensures commits and handles transactions
    with open("database/create_tables.sql", "r") as f:
        conn.execute(text(f.read()))
        print("Table creation succeeded.")

    if not csv_files:
        print("No CSV files found in data/raw/")
        exit()

    for file in sorted(csv_files):  # sort for nice chronological order
        print(f"Loading {file}")
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()

        # Rename to match PostgreSQL schema
        df = df.rename(columns={
            "deliverydate": "delivery_date",
            "hourending": "hour_ending",
            "settlementpoint": "settlement_point",
            "settlementpointprice": "settlement_point_price",
            "dstflag": "dst_flag"
        })

        try:
            df.to_sql("ercot_settlement_prices", conn, if_exists="append", index=False, method="multi")
            print(f"{len(df)} rows inserted from {file}")
            os.remove(file)  # Remove only after successful insert
            print(f"Removed {file} after successful load.")
        except SQLAlchemyError as e:
            print(f"Skipping {file} due to error: {e}")
            conn.rollback()
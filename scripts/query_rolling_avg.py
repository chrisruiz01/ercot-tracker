import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("POSTGRES_URI")
engine = create_engine(db_url)

# SQL query for 7-day rolling average
query = """
SELECT 
    settlement_point,
    delivery_date,
    hour_ending,
    settlement_point_price,
    ROUND(AVG(settlement_point_price) OVER (
        PARTITION BY settlement_point, hour_ending
        ORDER BY delivery_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_7_day_avg
FROM ercot_settlement_prices
ORDER BY settlement_point, delivery_date, hour_ending;
"""

# Load query results into pandas DataFrame
df = pd.read_sql(query, engine)

# Preview top rows
print(df.head())

# Optional: Save to CSV
df.to_csv("outputs/rolling_7_day_avg.csv", index=False)

print("Query complete and results saved to outputs/rolling_7_day_avg.csv")

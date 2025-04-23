import subprocess
from datetime import datetime

print("Running daily ERCOT data pipeline...")

# Step 1: Run fetch_data.py (make sure it fetches only today's file)
subprocess.run(["python", "scripts/fetch_data.py"])

# Step 2: Run load_to_db.py 
subprocess.run(["python", "scripts/load_to_db.py"])

# Step 3: Run query_rolling_avg.py to refresh output CSV
subprocess.run(["python", "scripts/query_rolling_avg.py"])

print(f"Pipeline finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
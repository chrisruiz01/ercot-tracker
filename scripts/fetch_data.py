import os
import requests
import zipfile
import io
import glob
import shutil
import pandas as pd
from fetch_latest_doc_id import get_latest_doclookup_id


raw_dir = "data/raw"
tmp_dir = "data/tmp"
os.makedirs(raw_dir, exist_ok=True)

# Get the latest doclookupId
doc_id = get_latest_doclookup_id()
if not doc_id:
    print("Skipping fetch - no new doclookupId found.")
    exit()
    
url = f"https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={doc_id}"
print(f"Fetching: {url}")

response = requests.get(url)
if response.status_code == 200:
    try:
        # Clear tmp dir
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir, exist_ok=True)

        # Extract to tmp folder
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(tmp_dir)
            print(f"Extracted ZIP")

        # Find CSV inside tmp folder
        csv_files = glob.glob(os.path.join(tmp_dir, "*.csv"))
        if csv_files:
            original_path = csv_files[0]

            # Detect actual DeliveryDate from inside the file
            df = pd.read_csv(original_path, nrows=1)
            actual_date = pd.to_datetime(df["DeliveryDate"].iloc[0])
            actual_date_str = actual_date.strftime("%Y%m%d")

            renamed_path = os.path.join(raw_dir, f"{actual_date_str}_da_spp.csv")
            if not os.path.exists(renamed_path):
                shutil.move(original_path, renamed_path)
                print(f"Renamed to: {renamed_path}")
            else:
                print(f"Already exists: {renamed_path}")
        else:
            print(f"No CSV found in ZIP")

        # Clean up tmp folder
        shutil.rmtree(tmp_dir)

    except zipfile.BadZipFile:
        print(f"Skipped - content is not a ZIP file.")
else:
    print(f"Failed to fetch. Status: {response.status_code}")
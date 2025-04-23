from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
import os
import requests 
import zipfile 
import io 
import shutil
import glob 
from datetime import datetime 

# Setup 
raw_dir = "data/raw"
tmp_dir = "data/tmp"
os.makedirs(raw_dir, exist_ok=True)

def get_recent_doclookup_ids(limit=30):
    url = "https://www.ercot.com/mp/data-products/data-product-details?id=NP4-190-CD"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    # Wait for JS content to load
    driver.implicitly_wait(3)

    doc_ids = []
    links = driver.find_elements(By.TAG_NAME, "a")

    for link in links:
        href = link.get_attribute("href")
        if href and "mirDownload?doclookupId=" in href:
            row = link.find_element(By.XPATH, "..").find_element(By.XPATH, "..")
            if "zip" in row.text.lower():
                doc_id = href.split("doclookupId=")[1]
                if doc_id not in doc_ids:
                    doc_ids.append(doc_id)
        if len(doc_ids) >= limit:
            break

    driver.quit()
    return doc_ids 

def download_and_extract(doc_id):
    url = f"https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={doc_id}"
    print(f"Fetching: {url}")
    response = requests.get(url)

    if response.status_code == 200:
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(tmp_dir)
                csv_files = glob.glob(os.path.join(tmp_dir, "*.csv"))
                if csv_files:
                    original_path = csv_files[0]

                    # Step 1: Load just the first line of the file to get the delivery date
                    import pandas as pd
                    df = pd.read_csv(original_path, nrows=1)
                    if "DeliveryDate" in df.columns:
                        delivery_date_str = pd.to_datetime(df["DeliveryDate"][0]).strftime("%Y%m%d")
                    else:
                        # fallback to filename if something goes wrong
                        filename = os.path.basename(original_path)
                        parts = filename.split(".")
                        delivery_date_str = parts[3] if len(parts) > 3 else datetime.today().strftime("%Y%m%d")
                    
                    renamed_path = os.path.join(raw_dir, f"{delivery_date_str}_da_spp.csv")
                    if not os.path.exists(renamed_path):
                        shutil.move(original_path, renamed_path)
                        print(f"Saved: {renamed_path}")
                    else:
                        print(f"Already exists: {renamed_path}")
        except zipfile.BadZipFile:
            print("Skipping - Not a valid ZIP file.")
        shutil.rmtree(tmp_dir)
    else:
        print(f"Failed to download {doc_id}: Status {response.status_code}")

# Run backfill 
if __name__ == "__main__":
    doc_ids = get_recent_doclookup_ids(limit=30)
    print(f"Found {len(doc_ids)} ZIPs to backfill.")
    for i, doc in enumerate(doc_ids, 1):
        print(f"{i:2}. doclookupId: {doc}")
    for doc_id in doc_ids:
        download_and_extract(doc_id)

    print("Backfill complete. Run load_to_db.py next.")

    
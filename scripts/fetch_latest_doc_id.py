from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import TimeoutException, WebDriverException
import time 

def get_latest_doclookup_id():
    url = "https://www.ercot.com/mp/data-products/data-product-details?id=NP4-190-CD"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service("chromedriver.exe")
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        time.sleep(3)  # wait for JS to load page content
    except WebDriverException as e:
        print("ChromeDriver launch failed:", e)
        return None

    links = driver.find_elements(By.TAG_NAME, "a")
    
    print("Scanning page links...")
    for link in links:
        href = link.get_attribute("href")
        print("Found:", href)
        
        if href and "mirDownload?doclookupId=" in href:
            try:
                # Check if nearby text indicates this is a ZIP file
                parent = link.find_element(By.XPATH, "..")  # go to parent td
                row = parent.find_element(By.XPATH, "..")   # go to parent tr
                if "zip" in row.text.lower():  # look for 'zip' in the whole row text
                    doc_id = href.split("doclookupId=")[1]
                    driver.quit()
                    return doc_id
            except Exception as e:
                print(f"Error reading row context: {e}")
                continue 
                
    driver.quit()
    print("No doclookupId ZIP link found on the page.")
    return None 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# --- CONFIGURE THESE ---
CASE_TYPE = "W.P.(C)"
CASE_NUMBER = "6768"
CASE_YEAR = "2025"

def fetch_case_data(case_type, case_number, case_year):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Comment this line if you want to see the browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    try:
        # --- STEP 1: LOAD PAGE ---
        driver.get("https://delhihighcourt.nic.in/app/get-case-type-status")
        wait.until(EC.presence_of_element_located((By.NAME, "case_type")))

        # --- STEP 2: FILL FORM FIELDS ---
        Select(driver.find_element(By.NAME, "case_type")).select_by_visible_text(case_type)
        driver.find_element(By.NAME, "case_number").clear()
        driver.find_element(By.NAME, "case_number").send_keys(case_number)
        Select(driver.find_element(By.NAME, "case_year")).select_by_visible_text(case_year)

        # --- STEP 3: HANDLE CAPTCHA (text-based) ---
        captcha_code = driver.find_element(By.ID, "captcha-code").text.strip()
        driver.find_element(By.ID, "captchaInput").clear()
        driver.find_element(By.ID, "captchaInput").send_keys(captcha_code)

        # --- STEP 4: SUBMIT FORM ---
        search_btn = wait.until(EC.element_to_be_clickable((By.ID, "search")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_btn)
        time.sleep(0.5)
        search_btn.click()

        # --- STEP 5: WAIT FOR RESULTS TO LOAD ---
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # --- STEP 6: SCRAPE RESULTS ---
        result = {}
        table = soup.find("table", id="caseTable")
        if table:
            tbody = table.find("tbody")
            rows = tbody.find_all("tr")
            if rows:
                cols = [td.get_text(strip=True) for td in rows[0].find_all("td")]
                # Adjust indices as per actual table structure
                result["serial_no"] = cols[0] if len(cols) > 0 else ""
                result["case_type_status"] = cols[1] if len(cols) > 1 else ""
                result["parties"] = cols[2] if len(cols) > 2 else ""
                result["listing_date_court_no"] = cols[3] if len(cols) > 3 else ""
                # Find latest order/judgment PDF link if present
                pdf_link = rows[0].find("a", href=True)
                result["latest_order_pdf"] = pdf_link["href"] if pdf_link else ""
            else:
                raise Exception("No case data found for the given details.")
        else:
            raise Exception("No results table found. The case may not exist or the site layout has changed.")

        return result, driver.page_source

    finally:
        driver.quit()

# --- STEP 7: PRINT STRUCTURED DATA ---
results, raw_html = fetch_case_data(CASE_TYPE, CASE_NUMBER, CASE_YEAR)

if results:
    print("\nStructured Case Data (for Flask app):\n")
    print(results)
else:
    print("No case found or invalid CAPTCHA/inputs.")

# If you want to use this in Flask, just return or jsonify(results)

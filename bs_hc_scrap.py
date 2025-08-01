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
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.binary_location = "/usr/bin/chromium"
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
                result["case_type_status"] = cols[1] if len(cols) > 1 else ""
                result["parties"] = cols[2] if len(cols) > 2 else ""
                result["listing_date_court_no"] = cols[3] if len(cols) > 3 else ""
                # Find latest order/judgment PDF link if present
                pdf_link_tag = rows[0].find("a", href=True)
                result["latest_order_page"] = pdf_link_tag["href"] if pdf_link_tag else ""
                result["latest_order_pdfs"] = []

                # --- STEP 7: FOLLOW ORDER LINK AND GET ALL PDF LINKS FROM TABLE ---
                if pdf_link_tag:
                    order_url = pdf_link_tag["href"]
                    if not order_url.startswith("http"):
                        order_url = "https://delhihighcourt.nic.in" + order_url
                    driver.get(order_url)
                    time.sleep(2)
                    order_soup = BeautifulSoup(driver.page_source, "html.parser")
                    pdf_links = []
                    # Find the correct table (usually id="caseTable" on the order page too)
                    order_table = order_soup.find("table", id="caseTable")
                    if order_table:
                        for row in order_table.find_all("tr"):
                            # Usually the PDF is in the "Order Link" column, so look for <a> with .pdf in href
                            for a in row.find_all("a", href=True):
                                href = a["href"]
                                if ".pdf" in href.lower():
                                    if not href.startswith("http"):
                                        href = "https://delhihighcourt.nic.in" + href
                                    pdf_links.append(href)
                    else:
                        print("No order table found on order page!")
                    result["latest_order_pdfs"] = pdf_links
            else:
                raise Exception("No case data found for the given details.")
        else:
            raise Exception("No results table found. The case may not exist or the site layout has changed.")

        return result, driver.page_source

    finally:
        driver.quit()

def get_case_types_and_years():
    driver = webdriver.Chrome(options=Options().add_argument("--headless"))
    driver.get("https://delhihighcourt.nic.in/app/get-case-type-status")
    select_type = Select(driver.find_element(By.NAME, "case_type"))
    types = [o.text for o in select_type.options if o.text.strip()]
    select_year = Select(driver.find_element(By.NAME, "case_year"))
    years = [o.text for o in select_year.options if o.text.strip()]
    driver.quit()
    return types, years

# --- STEP 7: PRINT STRUCTURED DATA ---
if __name__ == "__main__":
    results, raw_html = fetch_case_data(CASE_TYPE, CASE_NUMBER, CASE_YEAR)
    if results:
        print("\nStructured Case Data (for Flask app):\n")
        print(results)
    else:
        print("No case found or invalid CAPTCHA/inputs.")

# If you want to use this in Flask, just return or jsonify(results)

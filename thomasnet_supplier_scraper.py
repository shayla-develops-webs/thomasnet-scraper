# thomasnet_supplier_scraper.py (v1.1)
import time
import random
import os
import glob
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import hashlib
import json

# ------------------------
# SETTINGS (Customize these)
# ------------------------
# Target ThomasNet search URL (example provided, can be changed)
SEARCH_URL = "https://www.thomasnet.com/suppliers/northern-texas/all-cities/steel-79740205"

# Maximum number of leads to scrape (set high if you want all)
MAX_LEADS = 150

# CSV output columns - can add more if desired (email, website, etc.)
columns = [
    "company",
    "address",
    "business_phone",
    "cortera_score",
    "avg_mo_cortera_balance",
    "rep",
    "industry_category",
    "notes"
]

# Output folder
output_folder = "leads_output"
os.makedirs(output_folder, exist_ok=True)

# ------------------------
# LOAD PREVIOUS LEADS (avoid duplicates)
# ------------------------
def load_previous_leads():
    all_files = glob.glob(os.path.join(output_folder, "thomasnet_leads_*.csv"))
    if not all_files:
        return set()
    latest_file = max(all_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    return set(zip(df['company'], df['business_phone']))

existing_leads = load_previous_leads()

# ------------------------
# SAVE LEADS FUNCTION
# ------------------------
def save_leads_to_csv(leads, csv_filename):
    """Save leads to CSV file"""
    if leads:
        df = pd.DataFrame(leads, columns=columns)
        df.to_csv(csv_filename, index=False, encoding="utf-8")
        print(f"✓ {len(leads)} leads saved to {csv_filename}")
        return True
    else:
        print("No leads to save")
        return False

# ------------------------
# INITIALIZE SELENIUM WITH SEPARATE PROFILE
# ------------------------
def initialize_driver():
    options = Options()
    selenium_profile_path = os.path.join(os.getcwd(), "thomasnet_selenium_profile")
    print(f"Using separate Selenium profile: {selenium_profile_path}")

    options.add_argument(f"--user-data-dir={selenium_profile_path}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("Chrome driver initialized successfully!")
        return driver
    except Exception as e:
        print(f"Failed to initialize Chrome driver: {e}")
        return None

# ------------------------
# CHECK IF LOGGED IN
# ------------------------
def is_logged_in(driver, wait_time=2):
    try:
        # Wait a moment for page to load
        time.sleep(wait_time)
        
        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower()

        
        if any(indicator in current_url for indicator in ['dashboard', 'account', 'profile']):
            print("Login detected via URL!")
            return True

        
        if 'login' in current_url and any(indicator in page_source for indicator in ['sign in', 'email', 'password']):
            print("Still on login page")
            return False

        
        if any(indicator in page_source for indicator in ['sign out', 'logout', 'my account', 'dashboard']):
            print("Login detected via page content!")
            return True

        
        login_indicators = [
            "//a[contains(@href, 'account') and not(contains(@href, 'login'))]",
            "//button[contains(text(), 'Sign Out')]",
            "//a[contains(text(), 'Sign Out')]",
            "//*[contains(text(), 'My Account')]",
            "//*[contains(text(), 'Dashboard')]",
            "//a[contains(@href, 'logout')]"
        ]

        for indicator in login_indicators:
            try:
                element = driver.find_element(By.XPATH, indicator)
                if element.is_displayed():
                    print(f"Login detected via element: {indicator}")
                    return True
            except:
                continue

        print("No clear login indicators found.")
        return False

    except Exception as e:
        print(f"Error checking login status: {e}")
        return False

# ------------------------
# MANUAL LOGIN PROCESS
# ------------------------
def handle_login(driver):
    print("\n" + "="*60)
    print("LOGIN TO THOMASNET REQUIRED")
    print("="*60)
    print("A Chrome window has opened.")
    print("Please manually log in to ThomasNet in the browser.")
    print("When ready, type 'done' and press ENTER to continue.")
    print("Or type 'check' to verify if you're already logged in.")
    print("="*60)

    driver.get("https://www.thomasnet.com/account/login")
    
    while True:
        user_input = input("\nType 'done' when logged in, or 'check' to verify login status: ").strip().lower()
        
        if user_input == 'check':
            print("Checking login status...")
            if is_logged_in(driver, wait_time=60):
                print("✓ Login verified! You can proceed with scraping.")
            else:
                print("✗ Not logged in yet. Please complete the login process.")
                
        elif user_input == 'done':
            print("Verifying login status...")
            
            for attempt in range(5):  
                if is_logged_in(driver, wait_time=60):
                    print("✓ Login verified! Proceeding with scraping...")
                    return True
                else:
                    print(f"Still checking login status... (attempt {attempt + 1}/5)")
                    time.sleep(5)  
            
            
            retry = input("Login not detected. Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return False
                
        else:
            print("Please type either 'done' or 'check'")

# ------------------------
# JSON HASH HELPER
# ------------------------
def get_json_hash(driver):
    try:
        data = driver.execute_script("return JSON.stringify(window.__NEXT_DATA__.props.pageProps)")
        return hashlib.md5(data.encode()).hexdigest()
    except:
        return None

# ------------------------
# SCRAPER FUNCTION
# ------------------------
def scrape_thomasnet(driver):
    leads = []

    print(f"Navigating to target URL...")
    driver.get(SEARCH_URL)
    time.sleep(random.uniform(5, 7))

    page_index = 1
    while True:
        print(f"\n--- Scraping page {page_index} ---")

        # Wait for JSON data
        for attempt in range(10):
            raw_json = driver.execute_script("return window.__NEXT_DATA__.props.pageProps")
            if raw_json.get("companies"):
                break
            time.sleep(0.5)
        else:
            print(f"[WARNING] No companies found on page {page_index}")
            break

        companies = raw_json.get("companies", [])
        print(f"Found {len(companies)} companies on page {page_index}")

        for company in companies:
            if len(leads) >= MAX_LEADS:
                print(f"Reached maximum leads limit ({MAX_LEADS})")
                break

            company_name = company.get("name", "N/A")
            address_info = company.get("address", {})
            address_parts = [
                address_info.get("address1", ""),
                address_info.get("address2", ""),
                address_info.get("city", ""),
                address_info.get("state", ""),
                address_info.get("zip", ""),
                address_info.get("country", "")
            ]
            address = ", ".join([part for part in address_parts if part])
            phone = company.get("primaryPhone", "N/A")

            if (company_name, phone) in existing_leads or any(l[0] == company_name and l[2] == phone for l in leads):
                print(f"Skipping duplicate: {company_name}")
                continue

            leads.append([
                company_name,
                address,
                phone,
                "",  # cortera_score
                "",  # avg_mo_cortera_balance
                778002737,  # rep
                "",  # industry_category
                ""   # notes
            ])
            print(f"✓ Added: {company_name} | {phone}")

        # Save progress after each page
        if leads and len(leads) % 25 == 0:  # Save every 25 leads (1 page)
            temp_filename = csv_filename.replace('.csv', f'_temp_page{page_index}.csv')
            save_leads_to_csv(leads, temp_filename)
            print(f"Progress saved: {len(leads)} leads so far")

        if len(leads) >= MAX_LEADS:
            print(f"Reached target of {MAX_LEADS} leads!")
            break

        # Navigate to next page
        print(f"Attempting to navigate to next page...")
        old_hash = get_json_hash(driver)
        next_page_clicked = False

        next_page_methods = [
            f"//button[@aria-label='Results Page {page_index + 1}']",
            f"//button[text()='{page_index + 1}']",
            "//button[contains(text(), 'Next')]",
            "//a[contains(text(), 'Next')]",
            f"//a[text()='{page_index + 1}']"
        ]

        for method in next_page_methods:
            try:
                next_button = driver.find_element(By.XPATH, method)
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_button)
                next_page_clicked = True
                print(f"✓ Clicked next page button")
                break
            except:
                continue

        if not next_page_clicked:
            print("No next page found. Scraping complete.")
            break

        # Wait for JSON to update with fallback refresh
        for attempt in range(20):
            time.sleep(0.5)
            new_hash = get_json_hash(driver)
            if new_hash != old_hash:
                print("Page JSON updated!")
                break
        else:
            print("JSON did not update, performing full page refresh...")
            driver.refresh()
            time.sleep(random.uniform(5, 7))

        sleep_time = random.uniform(4, 7)
        print(f"Waiting {sleep_time:.1f} seconds before scraping next page...")
        time.sleep(sleep_time)
        page_index += 1

    return leads

# ------------------------
# MAIN EXECUTION
# ------------------------
if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(output_folder, f"thomasnet_leads_{timestamp}.csv")
    leads = [] 

    print("="*60)
    print("THOMASNET LEAD SCRAPER")
    print("="*60)

    driver = initialize_driver()
    if not driver:
        print("Failed to initialize Chrome driver. Exiting.")
        exit(1)

    try:
        if not is_logged_in(driver):
            if not handle_login(driver):
                print("Login failed. Exiting...")
                driver.quit()
                exit(1)

        print("\nStarting lead scraping process...")
        leads = scrape_thomasnet(driver)

    except KeyboardInterrupt:
        print(f"\nScraping interrupted by user. Scraped {len(leads)} leads so far.")
    except Exception as e:
        print(f"\nScraper failed with error: {e}")
        print(f"Scraped {len(leads)} leads before failure.")
    finally:
        # Always try to save whatever leads we got
        if leads:
            save_leads_to_csv(leads, csv_filename)
            print(f"\n✓ SUCCESS! Final save completed.")
        else:
            print("Creating empty CSV with headers...")
            pd.DataFrame(columns=columns).to_csv(csv_filename, index=False, encoding="utf-8")
        
        print("\nClosing browser...")
        if driver:
            try:
                driver.quit()
            except:
                print("Warning: Error closing browser, but continuing...")
        print("Done!")
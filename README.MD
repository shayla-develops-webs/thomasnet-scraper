# ThomasNet JSON Scraper

**Author:** Shayla Rodgers  
**Website:** [codedbyshay](https://codedbyshay.com)  
**GitHub:** [Shayla-develops-webs](https://github.com/Shayla-develops-webs)

---

## Overview

The ThomasNet JSON Scraper is a Python script that extracts company information from ThomasNet supplier search results, including:

- Company Name
- Address
- Phone Number

Additional fields like email, website, or notes can also be added. The scraper avoids duplicates, supports multiple runs per day, and saves results into a timestamped CSV file.

This script is designed for educational and non-commercial purposes, with clear credit to Shayla Rodgers.

---

## Features

- Scrapes any ThomasNet supplier search URL.
- Avoids duplicate leads using previous CSV data.
- Saves output in a clean CSV format with customizable columns.
- Handles manual login for ThomasNet.
- Can run multiple times per day.
- Open-source with credit to the original author.

---

## Requirements

- Python 3.9 or higher
- Google Chrome installed
- Python packages:
  ```bash
  pip install selenium pandas webdriver-manager
  ```

## Installation

Clone the repository:

```bash
git clone https://github.com/Shayla-develops-webs/thomasnet-supplier-scraper.git
cd thomasnet-supplier-scraper
```

Install required Python packages

Optional: create and activate a venv first

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Ensure pip is up-to-date

python -m pip install --upgrade pip

Then Install

python -m pip install -r .\requirements.txt

## Usage

Open the script thomasnet_supplier_scraper.py in a text editor.

Update the following settings:

SEARCH_URL = "https://www.thomasnet.com/suppliers/..." # Replace with any valid ThomasNet supplier search URL
MAX_LEADS = 75 # Maximum number of leads to scrape

Run the scraper:

python thomasnet_json_scraper.py

When prompted, manually log in to ThomasNet in the Chrome window.

Wait for the script to complete. Output CSV files are saved in leads_output/.

## Customization

Columns: Modify the columns list in the script to include additional fields such as email or website.

Output folder: Change output_folder to save CSV files in a different folder.

Leads limit: Adjust MAX_LEADS to scrape more or fewer leads.

Search URL: Replace SEARCH_URL with any valid ThomasNet supplier search link to scrape different suppliers.

## Contribution

I welcome contributions via pull requests. If you want to improve the scraper:

Fork the repository.

Create a new branch for your feature or fix.

Make your changes and commit.

Push your branch and submit a pull request.

Important: Any updates must credit Shayla Rodgers for the original work.

## License

Non-Commercial Open-Source License

Users may use, modify, and adapt this script for personal or educational purposes only.

Redistribution for profit or commercial purposes is prohibited.

Credit must always be given to Shayla Rodgers.

## Notes

The script relies on Selenium and Chrome; ensure your Chrome version is compatible with webdriver-manager.

You can run the script multiple times per day; duplicates are automatically skipped.

If the JSON data does not load, the script will refresh the page and retry.

The scraper extracts basic company data by default but can be extended with more fields if required.

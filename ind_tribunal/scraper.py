import os
import json
import logging
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from db_manager import DatabaseManager
from pdf_downloader import PDFDownloader
from datetime import datetime
import re




date_pattern = r"dated (\d{2}[-.]\d{2}[-.]\d{4})"
case_number_pattern = r"(ID No\. \d+ of \d+|Ref\. No\.\d+ of \d+)"
petitioner_pattern = r"title as (.*?) Vs|between (.*?) and"
respondent_pattern = r"Vs (.*?)(,| in term| and|$)|and (.*)$"


class Scraper:
    def __init__(self, config):
        self.config = config
        self.db_manager = DatabaseManager()
        self.pdf_downloader = PDFDownloader(config.PDF_DIR)




    def setup_browser(self):
        options = webdriver.ChromeOptions()
        return webdriver.Chrome(options=options)




    def select_date_range_and_search(self, driver):
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, self.config.MONTH_INPUT_ID)))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, self.config.YEAR_INPUT_ID)))

        month_input = driver.find_element(By.ID, self.config.MONTH_INPUT_ID)
        month_input.clear()
        month_input.send_keys(self.config.START_DATE)

        year_input = driver.find_element(By.ID, self.config.YEAR_INPUT_ID)
        year_input.clear()
        year_input.send_keys(self.config.END_DATE)

        search_button = driver.find_element(By.ID, self.config.SEARCH_BUTTON_ID)
        search_button.click()





    async def scrape_results_page(self, driver):
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'views-table')))

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        headers = self.extract_headers(soup)

        results = []
        rows = soup.select('tbody tr')
        
        session = self.pdf_downloader.create_session(driver)

        async with self.db_manager.get_connection() as db:
            for row in rows:
                row_data = self.extract_row_data(row, headers)
                case_info = self.extract_case_info(row_data, headers)
                pdf_link = row.select_one('a[href$=".pdf"]')
                if pdf_link and 'href' in pdf_link.attrs:
                    pdf_url = urljoin(self.config.URL, pdf_link['href'])
                    filename = os.path.basename(pdf_link['href'])
                    file_path = self.pdf_downloader.download(session, pdf_url, filename)
                    if file_path:
                        row_data['PDF_File_Path'] = file_path
                        case_info["pdf_link"] = os.path.abspath(file_path)
                        case_info["filename"] = filename
                
                await self.db_manager.store_metadata(case_info)
                
                results.append(row_data)
                logging.info(json.dumps(row_data, indent=2))

        return headers, results





    def extract_headers(self, soup):
        header_row = soup.select_one('thead tr')
        return [th.text.strip() for th in header_row.find_all('th')] if header_row else []





    def extract_row_data(self, row, headers):
        cols = row.find_all('td')
        row_data = {}
        for i, col in enumerate(cols):
            if i < len(headers):
                row_data[headers[i]] = col.text.strip()
            else:
                row_data[f'Extra_Column_{i - len(headers) + 1}'] = col.text.strip()
        return row_data






    def extract_case_info(self, row_data, headers):
        case_info = {}
        title = row_data.get(headers[1], "")
        date, caseno, petitioner, respondent = self.extract_details(title)
        casename = petitioner + ' vs ' + respondent
        case_info = {
            "casename": casename,
            "date": date,
            "petitioner": petitioner,
            "respondent": respondent,
            "case_number": caseno,
        }
        print(case_info)
        return case_info






    def extract_judges(self, judge_string):
        return [name.strip() for name in judge_string.split('&') if name.strip()]






    def format_date(self, date_str):
        try:
            # Replace separators with hyphen to normalize the format
            date_str = date_str.replace('.', '-')
            # Parse the date and format it to dd-mm-yyyy
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
            return date_obj.strftime("%d-%m-%Y")
        except ValueError:
            return "Invalid Date" 





    def extract_petitioner_respondent(self, text):
        if "v/s" in text:
            petitioner, respondent = text.split("v/s", 1)
        elif "vs" in text:
            petitioner, respondent = text.split("vs", 1)
        else:
            petitioner, respondent = text, text
        return petitioner.strip(), respondent.strip()
    

    def extract_details(self, string):
        date = re.search(date_pattern, string)
        case_number = re.search(case_number_pattern, string)
        petitioner = re.search(petitioner_pattern, string)
        respondent = re.search(respondent_pattern, string)
        if not date:
            return "None", case_number.group(0), petitioner.group(1), respondent.group(1)
        
        formatted_date = self.format_date(date.group(1))
        return formatted_date, case_number.group(0), petitioner.group(1), respondent.group(1)


    async def run(self):
        os.makedirs(self.config.PDF_DIR, exist_ok=True)

        driver = self.setup_browser()
        driver.get(self.config.URL)

        # self.select_date_range_and_search(driver)
        headers, results = await self.scrape_results_page(driver)
        driver.quit()
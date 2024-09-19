import os
import time
from datetime import timedelta
from selenium.webdriver.support.ui import Select
from Base import (
    initialize_driver,
    click_element_xpath,
    get_element_xpath,
    get_list_xpath,
)
from db import get_judge, update_judge_status, add_hc_record
from helpers import list_pdf_files
from dotenv import load_dotenv


load_dotenv()
PDF_DIR = os.getenv("PDF_DIR")
DATE_FORMAT = "%d/%m/%Y"


# Main scrapping function for batching
def crawl_gj_hc_batch_wise(container_client):
    try:
        judge = get_judge()
        name = judge.name
        hc_code = judge.code
        print(name)
        print(hc_code)
        doj = judge.doj
        held = judge.held
        start_date = doj.strftime(DATE_FORMAT)
        end_date = held.strftime(DATE_FORMAT)
        years_difference = held.year - doj.year
        print(f"From {start_date} to {end_date}")

        if years_difference <= 1:
            # Continue with your actions for exactly 2 years difference
            crawl_gj_hc_weekly(container_client, name, hc_code, start_date, end_date)
            update_judge_status(name)
        else:
            # Perform actions in batches of 2 years starting from doj
            print("Have to go with batches")
            current_date = doj
            while current_date <= held:
                batch_start_date = current_date.strftime(DATE_FORMAT)
                batch_end_date = (current_date + timedelta(days=365.25)).strftime(
                    DATE_FORMAT
                )

                print(f"Processing batch from {batch_start_date} to {batch_end_date}")

                # Perform actions for this batch
                crawl_gj_hc_weekly(
                    container_client, name, hc_code, batch_start_date, batch_end_date
                )

                # Move to the next batch
                current_date += timedelta(days=365.25)
            update_judge_status(name)
    except Exception as e:
        update_judge_status(name, "Failed")
        print(f"Exception in Guj HC batching - {e}")


# Scrapper function
def crawl_gj_hc_weekly(container_client, name, hc_code, start_date, end_date):
    try:
        driver = initialize_driver()
        driver.get("https://gujarathc-casestatus.nic.in/gujarathc/")

        # Clicking Hc Judge button to open judgment portal
        click_element_xpath(driver, '//*[@id="divinclude"]/div[2]/div[2]/div[1]/a')

        # Get from and to date inputs
        from_date = get_element_xpath(driver, '//*[@id="fromdate"]')
        to_date = get_element_xpath(driver, '//*[@id="todate"]')

        # Filling from and to dates
        driver.execute_script(
            "arguments[0].value = arguments[1]", from_date, start_date
        )
        driver.execute_script("arguments[0].value = arguments[1]", to_date, end_date)

        print("Dates filled")
        time.sleep(2)

        # Selecting Judge & Judgment type
        judge_type = Select(get_element_xpath(driver, '//*[@id="judgetype"]'))
        judge_type.select_by_value("active")

        judgment_type = Select(get_element_xpath(driver, '//*[@id="otype"]'))
        judgment_type.select_by_value("f")

        print("Judge and Judgment types selected")

        # Get Input to fill high court judge name
        highcourtjudge = get_element_xpath(driver, '//*[@id="hcjudgename"]')

        # Filling name by chars to trigger onkeypress event
        for char in name:
            highcourtjudge.send_keys(char)
            time.sleep(0.1)  # Adjust the delay as needed

        # Filling hidden input of judge code by executing js script
        script = f"document.getElementById('hcjudgename_hidden').value = '{hc_code}';"
        driver.execute_script(script)
        print("Judge details filled")

        # Clicking Go button
        click_element_xpath(driver, '//*[@id="gobuttonhcjudge"]')

        # Waiting for judgments to appear
        sleep_time = 100
        print(f"Waiting for {sleep_time} seconds")
        time.sleep(sleep_time)

        # Selecting all judgments from dropdown
        select_all = Select(
            get_element_xpath(driver, '//*[@id="master_length"]/label/select')
        )
        select_all.select_by_value("-1")

        print(get_element_xpath(driver, '//*[@id="toggeler"]/center/b').text)

        time.sleep(5)

        # Getting the list of judgments
        table = get_list_xpath(driver, '//*[@id="master"]/tbody/tr')
        total_judgments = len(table)
        print(f"Total length - {total_judgments}")
        if total_judgments == 1:
            print("No judgments found")
            return
        for i in range(1, total_judgments + 1):
            judge_name = get_element_xpath(
                driver, f"""//*[@id="master"]/tbody/tr[{i}]/td[3]"""
            )
            print(judge_name.text)
            # No link available hence have to click the anchor tag and download to default path
            click_element_xpath(driver, f"""//*[@id="master"]/tbody/tr[{i}]/td[8]/a""")

        print("PDFs Downloaded")

        # Upload PDfs to azure blob container
        pdf_files = list_pdf_files(PDF_DIR)
        for pdf in pdf_files:
            try:
                with open(f"{PDF_DIR}/{pdf}", "rb") as content:
                    container_client.upload_blob(pdf, content)
                add_hc_record(pdf)
            except Exception:
                print("Duplicate")
        # Delete file from directory to keep VM clean
        for pdf in pdf_files:
            file_path = f"{PDF_DIR}/{pdf}"
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"{pdf} deleted")
        print("Uploaded and cleaned")

    except Exception as e:
        print(f"Exception occured in Gujarat High Court Scrapping - {e}")

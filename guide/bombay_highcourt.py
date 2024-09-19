# Import necessary libraries and modules
import logging
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
from Base import (
    initialize_driver,
    click_element_xpath,
    get_element,
    get_element_xpath, 
    get_list_xpath,
    get_no_record,
)
from db import add_record
from azure_upload import upload_bhc_pdf_to_azure


# Function to extract captcha from img tag
def extract_captcha(driver):
    try:
        # Find the captcha image element
        captcha_img = driver.find_element(By.XPATH, "//img[@id='captchaimg']")

        # Extract captcha text from the src attribute
        captcha_src = captcha_img.get_attribute("src")
        captcha_text = captcha_src.split("=")[-1]

        return captcha_text

    except NoSuchElementException as e:
        print(f"Element not found while extracting captcha: {e}")
        return None


# Function to fill captcha input field
def fill_captcha(driver, captcha_text):
    try:
        # Find the captcha input field
        captcha_input = driver.find_element(By.ID, "captcha_code")

        # Fill captcha to input field
        captcha_input.send_keys(captcha_text)

        print("Filled captcha:", captcha_text)

    except NoSuchElementException as e:
        print(f"Element not found while filling captcha: {e}")


# Function to crawl Bombay High Court data for a specific date range
def crawl_bombay_highcourt(container_client, start_date, end_date):
    try:
        print("Crawling started for Bombay High Court")
        # Initialize the selenium driver
        driver = initialize_driver()

        # Open the Bombay High Court website
        driver.get("https://bombayhighcourt.nic.in/index.php")
        print("Entered in website")
        click_element_xpath(driver, "/html/body/div[3]/div/div/div[1]/ul/li[4]/a")
        print("Clicking on the Dropdown")
        click_element_xpath(
            driver, "/html/body/div[3]/div/div/div[1]/ul/li[4]/ul/li[3]/a"
        )
        print("Entered in Judgment Page")
        time.sleep(1)

        # Specify the start and end dates
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
        end_date = datetime.strptime(end_date, "%d-%m-%Y")

        # Find from date input
        from_date = get_element(driver, By.ID, "demo1")

        # Fill date to input field
        time.sleep(2)
        driver.execute_script(
            "arguments[0].value = arguments[1]",
            from_date,
            start_date.strftime("%d-%m-%Y"),
        )

        # Find to date input field
        to_date = get_element(driver, By.ID, "demo2")

        # Fill date to input field
        driver.execute_script(
            "arguments[0].value = arguments[1]", to_date, end_date.strftime("%d-%m-%Y")
        )
        print("Date added")

        # Extract captcha text
        captcha_text = extract_captcha(driver)

        if captcha_text:
            # Fill captcha
            fill_captcha(driver, captcha_text)

            print("Clicking submit button")
            click_element_xpath(
                driver,
                "/html/body/div[3]/div/div[2]/form/table/tbody/tr[2]/td/div[10]/input",
            )
        else:
            print("Failed to extract captcha for Bombay High Court")
            return 0
        # Attempt to find the "no record" element
        no_record = get_no_record(
            driver, "/html/body/div[3]/div/div/table[2]/tbody/tr/td"
        )

        if no_record:
            logging.info(f"No record found for {start_date} to {end_date}.")
            print(
                f"Crawling successful for {start_date} to {end_date} - no record found",
            )
            return 0

        # Attemt to find the "Invalid input"
        invalid_input = get_no_record(driver, "/html/body/blockquote/div")

        if invalid_input:
            logging.info(f"Invalid input given for {start_date} to {end_date}.")
            print(f"Invalid input given for {start_date} to {end_date}.")
            print(
                f"Crawling successful for {start_date} to {end_date} - Invalid input given."
            )
            return 0

        # Find all the <tr> tag in the <body> element
        single_rows = get_list_xpath(
            driver, "/html/body/div[3]/div/div/div/table/tbody/tr"
        )

        # Define the start and end indices
        start_index = 2
        end_index = len(single_rows) # Index of the last row
        print("Found all the judgments for Bombay High Court")

        length = len(single_rows) - 2
        print("Total Judgments ", length)

        # Empty array for saving PDF links
        pdf_links = []

        for index in range(start_index, end_index):
            # Try the first type of XPath
            xpath_expression1 = (
                f"/html/body/div[3]/div/div/div/table/tbody/tr[{index}]/td[4]/i/a"
            )
            try:
                element = get_element_xpath(driver, xpath_expression1)
                if element is not None:
                    pdf_link = element.get_attribute("href")
                    if pdf_link:
                        add_record(pdf_link)
                        print("pdf added")
                        pdf_links.append(pdf_link)
                        continue  # Move to the next iteration if successful with the first XPath
            except Exception as e:
                print(e)
                pass # Continue to the next attempt with the second XPath

            # Try the second type of XPath
            xpath_expression2 = (
                f"/html/body/div[3]/div/div/div/table/tbody/tr[{index}]/td[4]/a"
            )
            try:
                element = get_element_xpath(driver, xpath_expression2)
                if element is not None:
                    pdf_link = element.get_attribute("href")
                    if pdf_link:
                        add_record(pdf_link)
                        print("pdf added")
                        pdf_links.append(pdf_link)
            except ElementClickInterceptedException as e:
                print(f"Both XPath expressions failed for index {index}: {e}")

        # Loop through each PDF link and upload to Azure Blob Storage
        for pdf_link in pdf_links:
            upload_bhc_pdf_to_azure(pdf_link, container_client)

        print(f"Crawling successful for {start_date} to {end_date}.")
    except Exception as e:
        print(f"Bombay high court crawling failed - {e}")
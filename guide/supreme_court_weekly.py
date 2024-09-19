import logging
from selenium.webdriver.common.by import By
from Base import (
    initialize_driver,
    click_element_xpath,
    get_element,
    get_element_xpath,
    get_list_xpath,
    get_no_record,
)
from db import add_record


def crawl_sc_weekly(start_date, end_date):
    try:
        driver = initialize_driver()
        driver.get("https://main.sci.gov.in/judgments")
        print(f"Supreme Court scrapping started for {start_date} to {end_date} week")
        print("Clicking navbar")
        click_element_xpath(driver, '//*[@id="tabbed-nav"]/ul[2]/li[3]')
        # Find captcha element
        captcha = get_element(driver, By.XPATH, '//*[@id="cap"]/font')

        # Fill captcha to input field
        driver.find_element(By.ID, "ansCaptcha").send_keys(captcha.text)
        print("Filled captcha: " + captcha.text)

        # Find from date input field
        from_date = get_element(driver, By.ID, "JBJfrom_date")

        # Fill date to input field
        driver.execute_script(
            "arguments[0].value = arguments[1]", from_date, start_date
        )

        # Find to date input field
        to_date = get_element(driver, By.ID, "JBJto_date")

        # Fill date to input field
        driver.execute_script("arguments[0].value = arguments[1]", to_date, end_date)

        print("Clicking submit button")
        # Click submit button
        click_element_xpath(driver, '//*[@id="v_getJBJ"]')

        no_record = get_no_record(driver, '//*[@id="JBJ"]/div/div')

        if no_record:
            logging.info(f"No record found for {start_date} to {end_date} week")
            print(f"No record found for {start_date} to {end_date} week")
            return {
                "message": f"Crawling successful for {start_date} to {end_date} week - no record found",
                "error": "",
            }
        # Find all <tr> tags inside <tbody> element
        single_rows = get_list_xpath(driver, "//*[@id='JBJ']/table/tbody/tr")

        # Find last judgement from list of <tr> tags
        last_record_xpath = (
            "//*[@id='JBJ']/table/tbody/tr[" + str(len(single_rows) - 8) + "]/td[1]"
        )

        print(f"Found all the judgments - {len(single_rows)}")
        last_record = get_element_xpath(driver, last_record_xpath)
        print(last_record.text)

        judgement_index = 1
        for _ in range(1, int(len(single_rows) / 8)):
            # PDF Links
            judgement_index += 1
            pdf_link = get_element_xpath(
                driver,
                "//*[@id='JBJ']/table/tbody/tr["
                + str(judgement_index)
                + "]/td[3]/a[2]",
            ).get_attribute("href")
            add_record(pdf_link)
            judgement_index += 8

        print(f"Supreme Court Scrapping successful for {start_date} to {end_date} week")
    except Exception as e:
        print(f"Exception ocurred in Supreme Court Scrapping - {e}")

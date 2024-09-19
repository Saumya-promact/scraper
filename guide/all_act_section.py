import re
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Base import (
    initialize_driver,
    click_element_xpath,
    get_element,
    get_element_xpath,
    get_list,
)


# Main crawling function
def crawl_india_code():
    driver = initialize_driver()
    driver.get("https://www.indiacode.nic.in/")

    all_data = []

    try:
        # Click on browse central acts
        click_element_xpath(driver, "/html/body/header/div[4]/div/nav/ul[1]/li[4]/a")

        # Select Enactment date
        click_element_xpath(
            driver, "/html/body/header/div[4]/div/nav/ul[1]/li[4]/ul/li[4]/a"
        )

        # Select 100 limit
        click_element_xpath(
            driver, '//*[@id="browse_controls"]/form/select[3]/option[20]'
        )

        # Click update button
        click_element_xpath(driver, '//*[@id="browse_controls"]/form/input[3]')

        for k in range(9):
            # Get acts table
            tbody = WebDriverWait(driver, 40).until(
                EC.presence_of_element_located(
                    ('//*[@id="content"]/div/div/div[2]/div/table/tbody')
                )
            )

            # Get list of tr tags - acts
            all_acts = get_list(tbody, By.TAG_NAME, "tr")

            # Iterate through every acts
            for i in range(2, len(all_acts) + 1):
                sections_list = []
                # Act text Xpath
                act_index = (
                    f'//*[@id="content"]/div/div/div[2]/div/table/tbody/tr[{i}]/td[3]'
                )
                # Act text
                act_name = get_element_xpath(driver, act_index).text

                # Section view link
                sections_link = (
                    f'//*[@id="content"]/div/div/div[2]/div/table/tbody/tr[{i}]/td[4]/a'
                )
                # Click view sections
                click_element_xpath(driver, sections_link)

                section_info = get_element_xpath(
                    driver, '//*[@id="myTableActSection_info"]'
                ).text
                if section_info == "Showing 0 to 0 of 0 entries":
                    driver.back()
                    continue

                # Select 100 limit
                click_element_xpath(
                    driver,
                    '//*[@id="myTableActSection_length"]/label/select/option[4]',
                )

                # Get section table
                sections_body = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        ('//*[@id="myTableActSection"]/tbody')
                    )
                )

                # Get all the sections
                all_sections = get_list(sections_body, By.TAG_NAME, "tr")

                print(f"Act: {act_name}")

                # Iterating over each section
                for j in range(0, len(all_sections)):
                    section_name = get_element(
                        all_sections[j], By.XPATH, "td/div/a"
                    ).text
                    pattern = re.compile(r"repeal|omit", re.IGNORECASE)
                    if pattern.search(section_name):
                        continue
                    sections_list.append(section_name)
                all_data.append({"act": act_name, "sections": sections_list})
                driver.back()

            # Click next button
            get_element(
                driver,
                By.CSS_SELECTOR,
                "#content > div > div > div:nth-child(2) > div > div.panel-footer.text-center > a.pull-right",  # noqa: E501
            ).click()
            print(f"{100 * (k+1)} acts")

    except Exception as ex:
        print(f"Exception - {ex}")
        return f"Exception occurred - {str(ex)}"
    finally:
        # Quite driver
        driver.quit()
        # Write the data to the JSON file
        with open("all_acts_sections.json", "w") as json_file:
            json.dump(all_data, json_file, indent=4)
        print("Json file successfully written...")
    return all_data

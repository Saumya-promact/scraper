import json
from Base import (
    initialize_driver,
    get_element_xpath,
    get_list_xpath,
)
from selenium.webdriver.support.ui import Select
from db import update_judge_doj, add_judge
from fuzzycheck import find_similar_names


def scrap_gj_judges():
    try:
        driver = initialize_driver()
        driver.get("https://gujarathighcourt.nic.in/fcjs")
        print("Started scrapping Gujarat High Court Judges")

        select_all = Select(
            get_element_xpath(driver, '//*[@id="jlist_length"]/label/select')
        )
        select_all.select_by_value("100")
        judges_details = get_list_xpath(driver, '//*[@id="jlist"]/tbody/tr')

        print(len(judges_details))
        for i in range(3, 29):
            judge = get_element_xpath(
                driver,
                f'//*[@id="jlist"]/tbody/tr[{i}]/td/div/div/div[2]/span[1]',
            ).text

            details = get_element_xpath(
                driver,
                f'//*[@id="jlist"]/tbody/tr[{i}]/td/div/div/div[2]/span[2]',
            ).text

            name = judge.split("ble")[-1].strip()
            details = details.split("|")
            doj = details[1].split(":")[-1].strip()
            held = details[-1].split(":")[-1].strip()

            most_similar_judge = find_similar_names(name)
            if len(most_similar_judge) == 0:
                continue
            print(f"name - {name}")
            print(f"Db name - {most_similar_judge[0]}")
            print(f"doj = {doj}, held = {held}")
            update_judge_doj(most_similar_judge[0], doj, held)
            print()
    except Exception as e:
        print(f"Exception in scrapping judges {e}")


def add_judge_with_codes():
    with open("./fcj.json", "r") as judges_dict:
        data = json.load(judges_dict)
    for judge in data:
        add_judge(judge, data[judge], "High Court of Gujarat")

    print("Judges with Codes added")

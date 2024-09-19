from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


max_retries = 3
all_exceptions = (TimeoutException, StaleElementReferenceException)


# Initialize selenium driver
def initialize_driver():
    options = Options()
    options.add_argument("-headless")
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", "./pdfs")
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")

    driver = webdriver.Firefox(options=options)

    print("Firefox initialized in headless mode")
    return driver


# Click element
def click_element(driver, by, value):
    for _ in range(max_retries):
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((by, value))
            )
            driver.execute_script("arguments[0].click();", element)
            print("Clicked element")
            break
        except all_exceptions as e:
            print(f"Exception - {e} retrying")


# Get element with specific selector
def get_element(driver, by, value):
    for _ in range(max_retries):
        try:
            return WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((by, value))
            )

        except all_exceptions:
            print("Retrying")


def get_no_record(driver, value):
    try:
        element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, value))
        )
        print(element.text)
        return True
    except Exception:
        print("There are records")
        return False


# Get list of elements with specific selector
def get_list(driver, by, value):
    for _ in range(max_retries):
        try:
            return WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except all_exceptions as e:
            print(f"Exception - {e} retrying")


# Click element with XPATH
def click_element_xpath(driver, value):
    click_element(driver, By.XPATH, value)


# Get element with XPATH
def get_element_xpath(driver, value):
    return get_element(driver, By.XPATH, value)


# Get list of elements with XPATH
def get_list_xpath(driver, value):
    return get_list(driver, By.XPATH, value)


# Get previous week's date for scrapping
def get_previous_week_dates(current_datetime):
    # Calculate the previous Saturday
    previous_saturday = current_datetime - timedelta(
        days=current_datetime.weekday() + 1
    )

    # Calculate the start and end dates of the previous week
    start_date = previous_saturday - timedelta(days=6)
    end_date = previous_saturday

    # Return the start and end dates in dd-mm-yyyy format
    return start_date.strftime("%d-%m-%Y"), end_date.strftime("%d-%m-%Y")

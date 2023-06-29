import time
import logging
import pandas as pd
from math import ceil
from datetime import datetime
from decouple import config
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

USERNAME = config('USERNAME')
PASSWORD = config('PASSWORD')
start_url = "https://linkedin.com"
columns = ["date", "search_key", "search_count", "id", "title", "company", "location", "num_applicants", "pay",
           "length", "level", "size", "industry", "details", 'last_updated']

page_timeout = 30
click_timeout = 10
num_retries = 3
first_errors = 0
second_errors = 0

def logging_in():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options)

    logging.info(f"Logging into LinkedIn as {USERNAME}...")
    for attempt in range(num_retries):
        try:
            driver.get(start_url)
            driver.find_element(by=By.ID, value="session_key").send_keys(USERNAME)
            driver.find_element(by=By.ID, value="session_password").send_keys(PASSWORD)
            driver.find_element(by=By.XPATH, value="//button[normalize-space()='Sign in']").click()
            break
        except: logging.info(f"Issues navigating landing page, attempt {attempt+1}/{num_retries}")
    logging.info("Log in completed. Beginning to scrape jobs...")
    return driver

def scrape_page(driver, location, keyword, remote, date_posted, search_count):
    job_list = []
    search_url = f"https://www.linkedin.com/jobs/search/?f_TPR={date_posted}&f_WT={remote}&geoId=101174742&keywords={keyword}&location={location}&start={search_count}"
    driver.get(search_url)
    driver.implicitly_wait(page_timeout)

    total_count = driver.find_element(by=By.XPATH, value="//div[@class='jobs-search-results-list__subtitle']//span").text
    total_count = int(total_count.split(" ")[0].replace(",", ""))
    logging.info(f"Currently scraping page {round(search_count/25) + 1} of {ceil(total_count/25)} for {keyword}'s with {total_count} results...")

    for attempt in range(num_retries):
        try:
            list_results = driver.find_element(by=By.XPATH, value="//ul[@class='scaffold-layout__list-container']").find_elements(by=By.TAG_NAME, value='li')
            result_ids = [result.get_attribute('id') for result in list_results if result.get_attribute('id') != '']
            break
        except: time.sleep(click_timeout)

    for id in result_ids:
        try:
            job_li = driver.find_element(by=By.ID, value=id)
            job_id = job_li.get_attribute("data-occludable-job-id")
            element = driver.find_element(by=By.XPATH, value=f"//div[@data-job-id={job_id}]")

            driver.execute_script("arguments[0].scrollIntoView()", element)
            ActionChains(driver).move_to_element(element).click().perform()
        except: continue

        for attempt in range(num_retries):
            try:
                role = ""
                role = driver.find_element(by=By.XPATH, value="//h2[@class='t-24 t-bold jobs-unified-top-card__job-title']").text
                break
            except: time.sleep(click_timeout)

        for attempt in range(num_retries):
            try:
                company, location, updated, applicants = ["" for i in range(4)]
                top_card = driver.find_element(by=By.XPATH, value = "//div[@class='jobs-unified-top-card__primary-description']//div")
                content = top_card.text.split("·")
                try:
                    company = content[0].strip()
                    applicants = content[2].strip()
                except: pass

                try:
                    info = content[1].split("  ")
                    location = info[0].strip()
                    updated = info[1].strip()
                except: pass
                break
            except: time.sleep(click_timeout)

        for attempt in range(num_retries):
            try:
                length, pay, level = ["" for i in range(3)]
                description = WebDriverWait(driver, 20).until(
                    lambda x: x.find_element(by=By.XPATH, value="//div[@class='mt5 mb2']//ul//li[1]//span"))

                content = description.text
                if content != "":
                    content = content.split("·")
                    if len(content) == 1: length = content[0]
                    elif (len(content) >= 2) and ("$" in content[0]):
                        pay = content[0]
                        length = content[1]
                        if len(content) >= 3: level = content[2]
                    else:
                        length = content[0]
                        level = content[1]
                    break
                else: time.sleep(click_timeout)
            except: time.sleep(click_timeout)

        for attempt in range(num_retries):
            try:
                size, industry, details = ["" for i in range(3)]
                info = WebDriverWait(driver, 20).until(
                    lambda x: x.find_element(by=By.XPATH, value="//div[@class='mt5 mb2']//ul//li[2]//span"))

                data = info.text.split("·")
                if len(data) >= 2:
                    size = data[0]
                    industry = data[1]
                else: size = data[0]

                details = driver.find_element(by=By.XPATH, value="//div[@id='job-details']").text.replace("\n", "")
                break
            except: time.sleep(click_timeout)

        date_time = datetime.now().strftime("%d%b%Y-%H:%M:%S")
        job_list.append([date_time, keyword, search_count, job_id, role, company, location, applicants, pay, length, level, size, industry, details, updated])

    dataframe = pd.DataFrame(job_list)
    dataframe.to_csv(file_name, mode='a', index=False, header=False)
    job_list.clear()
    logging.info(f"Done scraping page {round(search_count/25) + 1} of {ceil(total_count/25)}")
    search_count += 25

    return search_count, total_count

# -------- main ----------------


time_now = datetime.today().strftime('%d-%b-%y_%H:%M:%S')
log_file = f"log/{time_now}.log"
file_name = f"data/JOB_DATA_{time_now}.csv"

logging.basicConfig(filename=log_file, filemode="w", level=logging.INFO, format="%(asctime)s  - %(levelname)s - %(message)s", force=True)
logging.info(f"Log file {log_file} successfully created.")
df = pd.DataFrame(list(), columns=columns)
df.to_csv(file_name, index=False)

driver = logging_in()
keyword, location, remote, date_posted = ["machine learning engineer", "Canada", "2", "r2592000"]
search_count = 0; total_count = 1

while(search_count < total_count) and (search_count != 1000):
    try:
        search_count, total_count = scrape_page(driver, location, keyword, remote, date_posted, search_count)
    except Exception as error:
        logging.error(f"(1) Error while loading results for {keyword} on page {round(search_count/25) + 1} of {ceil(total_count/25)}, retrying...")
        logging.error(error)
        first_errors += 1
        time.sleep(click_timeout)
        try:
            search_count, total_count = scrape_page(driver, location, keyword, remote, date_posted, search_count)
            logging.warning(f"Solved error for {keyword} on page {round(search_count/25)} of {ceil(total_count/25)}")
        except Exception as error:
            logging.error(f"(2) Error remains for {keyword}. Moving to the next page...")
            logging.error(error)
            second_errors += 1
            search_count += 25

driver.quit()

logging.info(f"LinkedIn job data scraping complete with {first_errors} first and {second_errors} second errors.")
logging.info(f"View final results structured in CSV format within the data directory.")
from random import random
import json
from time import sleep
from glob import glob
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import re

options = webdriver.ChromeOptions()
# options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# UserAgent값을 바꿔줍시다!
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

driver = webdriver.Chrome(options=options)


def collect_wines():
    wines = []
    print(driver.title)

    for page in range(1, 16):
        driver.get(f"https://www.ssg.com/disp/category.ssg?dispCtgId=6000099420&pageSize=100&page={page}")
        view = driver.find_element(by=By.ID, value="ty_thmb_view")
        items = view.find_elements(by=By.CLASS_NAME, value="cunit_info")

        for item in items:
            title = item.find_element(by=By.CLASS_NAME, value="tx_ko")
            texts = re.split('[\[\]\(\) ]', title.text)
            wines = wines + [text for text in texts if text != '']

    wines = set(wines)
    return list(wines)


def save_to_json(item: dict):
    name = f"{item.get('country')}-{item.get('name')}.json"

    print(f"[INFO] creating {name}")
    with open(f"./wine_info/{name}", 'w', encoding="UTF-8") as f:
        json.dump(item, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    wine_names = collect_wines()

    with open("emart.txt", "w", encoding="UTF-8") as f:
        f.writelines("\n".join(wine_names))

    driver.quit()

    print('test')

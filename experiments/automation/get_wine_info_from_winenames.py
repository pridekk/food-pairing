from random import random
import json
from time import sleep
from glob import glob
from types import SimpleNamespace

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import re
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# UserAgent값을 바꿔줍시다!
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

driver = webdriver.Chrome(options=options)


def collect_wines(wine_names):
    infos = {}
    for name in wine_names:
        driver.get("https://www.wine21.com/10_main/total_search.html")

        search = driver.find_element(by=By.ID, value="inputTotalSearch")

        search.send_keys(name, Keys.RETURN)

        item = driver.find_element(by=By.CLASS_NAME, value="search-result-item")

        if item.text != '':
            wine_info = None
            tags = item.find_elements(by=By.TAG_NAME, value="h3")

            for tag in tags:

                en_name = tag.find_element(by=By.CLASS_NAME, value="wine-name-en").text
                en_name = re.sub(",| |-", "", en_name)
                wine_name = re.sub(",| |-", "", name)

                if wine_name == en_name:
                    try:
                        tag.click()
                        wine_info = extract_wine_info(name)
                    except Exception as e:
                        print(f"[ERROR] Cannot get {name} wine info. Pass")

                    break

            if wine_info:
                print(wine_info)
                infos[name] = wine_info

    return infos


def exist(wine_info: dict):
    name = f"{wine_info.get('country')}-{wine_info.get('name')}.json"
    file = glob(f"./wine_info/{name}")

    if file:
        print(f"[INFO] {name} WINE INFO EXIST")
        return True
    return False


def extract_wine_info(wine_name):
    print(f"[INFO] Extract wine info of {wine_name}")
    try:
        wine_type = driver.find_element(by=By.CLASS_NAME, value="bagde-item").text
        name = driver.find_element(by=By.CLASS_NAME, value="wine-name").text
        en_name = driver.find_element(by=By.CLASS_NAME, value="wine-name-en").text
        price_from_importer = driver.find_element(by=By.CLASS_NAME, value="wine-price").text

        price_from_importer = price_from_importer.replace("빈티지별 가격보기", "").strip()
        wine_comp = driver.find_elements(by=By.XPATH, value="//div[@class='filter-grade']")
        sugar = len(wine_comp[0].find_elements(by=By.CLASS_NAME, value="on"))
        acidity = len(wine_comp[1].find_elements(by=By.CLASS_NAME, value="on"))
        body = len(wine_comp[2].find_elements(by=By.CLASS_NAME, value="on"))
        tannin = len(wine_comp[3].find_elements(by=By.CLASS_NAME, value="on"))

        detail = driver.find_element(by=By.CLASS_NAME, value="view-tab-inner")
        detail_title = detail.find_elements(by=By.TAG_NAME, value="dt")
        detail_info = detail.find_elements(by=By.TAG_NAME, value="dd")

        winery = ""
        main_grape = ""
        country = ""
        city = ""
        alcohol = ""
        serving_temp = ""
        recommend = ""

        for idx, title in zip(range(0, len(detail_title)), detail_title):
            title_text = title.text

            if "생산자" in title_text:
                winery = detail_info[idx].text
            elif "국가" in title_text:
                country = detail_info[idx].text.split(">")[0].strip()
                city = detail_info[idx].text.split(">")[-1].strip()
            elif "주요품종" in title_text:
                main_grape = detail_info[idx].text
            elif "알코올" in title_text:
                alcohol = detail_info[idx].text
            elif "음용온도" in title_text:
                serving_temp = detail_info[idx].text
            elif "추천음식" in title_text:
                recommend = detail_info[idx].text

        matching_elements = driver.find_elements(by=By.CLASS_NAME, value="view-wine-matching")
        pairings = []
        aromas = []

        for element in matching_elements:
            if element.text.startswith("아로마"):
                aromas = element.find_elements(by=By.TAG_NAME, value="p")
                aromas = ",".join(item.text for item in aromas)
                aromas = set([item.strip() for item in aromas.split(",") if len(item.strip()) > 1])
            elif element.text.startswith("음식매칭"):
                pairings = element.find_elements(by=By.TAG_NAME, value="p")
                pairings = ",".join(item.text for item in pairings)
                pairings = set([item.strip() for item in pairings.split(",") if len(item.strip()) > 1])

        return {
            'name': name.replace(",", " "),
            'en_name': en_name.replace(",", " "),
            'type': wine_type.replace(",", " "),
            'price_from_importer': price_from_importer.replace(",", " "),
            'sugar': sugar,
            'acidity': acidity,
            'body': body,
            'tannin': tannin,
            'winery': winery.replace(",", " "),
            'main_grape': main_grape.replace(",", "|"),
            'country': country.replace(",", " "),
            'city': city.replace(",", " "),
            'aromas': list(aromas),
            'pairings': list(pairings),
            'recommend': recommend.replace(",", "|"),
            'alcohol': alcohol.replace(",", " "),
            'serving_temp': serving_temp,
            'url': driver.current_url
        }
    except NoSuchElementException:
        print("f[ERROR] {wine_name}: Cannot extract Wine Info")
    return None


def save_to_json(item: dict):
    name = f"{item.get('country')}-{item.get('name')}.json"

    print(f"[INFO] creating {name}")
    with open(f"./wine_info/{name}", 'w', encoding="UTF-8") as f:
        json.dump(item, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":

    wine_list = []

    with open("wine_list.txt") as f:
        names = f.readlines()

    for name in names:
        wine_id, wine_name = name.split("\t")
        wine_list.append((wine_id, wine_name.replace("\n", "")))

    data = collect_wines([name[1] for name in wine_list])

    with open("wine_data_from_wine21.csv", "w", encoding="utf-8") as f:
        for name in wine_list:
            if name[1] in data:
                wine = SimpleNamespace(**data[name[1]])

                line = f"{name[0]}, {wine.name}, {wine.en_name}, {wine.type}, {wine.country}, {wine.winery}, {wine.main_grape}, {wine.body}, {wine.tannin}, {wine.sugar}, {wine.acidity}, {'|'.join(wine.aromas)},{'|'.join(wine.pairings)}, {wine.alcohol}, {wine.recommend}, {wine.url}\n"
                f.write(line)
    driver.quit()

    print('test')

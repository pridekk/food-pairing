from random import random
import json
from time import sleep
from glob import glob
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
driver = webdriver.Chrome()


def collect_wines():
    driver.get("https://www.wine21.com/13_search/wine_list.html")

    print(driver.title)
    done = False
    cnt = 722
    while not done:

        items = driver.find_elements(by=By.XPATH, value="//ul[@id='wine_list']/descendant::li")
        if cnt < len(items):
            location = items[cnt].location['y'] - 100
            driver.execute_script(f"window.scrollTo(0,{location})")
            item_name = items[cnt].find_element(by=By.TAG_NAME, value="h3").text
            items[cnt].click()
            sleep(random()*2)
            print(f"[INFO] CNT: {cnt}")
            info = extract_wine_info(item_name)
            if info:
                if exist(info):
                    print("[INFO] WINE INFO EXIST. SKIP PROCESSING")

                else:
                    save_to_json(info)

            cnt += 1
            driver.back()
            sleep(random()*2)
        else:
            more_button = driver.find_element(by=By.ID, value="wineListMoreBtn")
            more_button.click()

        sleep(1)


def exist(wine_info:dict):
    name = f"{wine_info.get('country')}-{wine_info.get('name')}.json"
    file = glob(f"./wine_info/{name}")

    if file:
        print(f"[INFO] {name} WINE INFO EXIST")
        return True
    return False


def extract_wine_info(wine_name):
    print(f"[INFO] Extract wine info of {wine_name}")
    try:
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
        winery = detail.find_elements(by=By.TAG_NAME, value="dd")[0].text
        main_grape = detail.find_elements(by=By.TAG_NAME, value="dd")[2].text
        country = detail.find_elements(by=By.TAG_NAME, value="dd")[1].text.split(">")[0].strip()
        city = detail.find_elements(by=By.TAG_NAME, value="dd")[1].text.split(">")[-1].strip()
        matching_elements = driver.find_elements(by=By.CLASS_NAME, value="wine-matching-list")
        pairings = []
        aromas = []
        if matching_elements:
            aromas = matching_elements[0].find_elements(by=By.TAG_NAME, value="p")
            aromas = ",".join(item.text for item in aromas)
            aromas = set([item.strip() for item in aromas.split(",") if len(item.strip()) > 1])

            if len(matching_elements) > 1:
                pairings = matching_elements[1].find_elements(by=By.TAG_NAME, value="p")
                pairings = ",".join(item.text for item in pairings)
                pairings = set([item.strip() for item in pairings.split(",") if len(item.strip()) > 1])

        return {
            'name': name,
            'en_name': en_name,
            'price_from_importer': price_from_importer,
            'sugar': sugar,
            'acidity': acidity,
            'body': body,
            'tannin': tannin,
            'winery': winery,
            'main_grape': main_grape,
            'country': country,
            'city': city,
            'aromas': list(aromas),
            'pairings': list(pairings),
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
    collect_wines()

    print('test')
import json
from time import sleep

from bs4 import BeautifulSoup
import requests
import csv
import random
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}


def get_wine_rating(wine_name):
    query_string = "+".join(wine_name.split(" "))

    response = requests.get(f"https://www.vivino.com/search/wines?q={query_string}", headers=headers)

    print(response.status_code)

    html = BeautifulSoup(response.text, 'html.parser')

    search_result = html.find(attrs={'class': 'search-results-list'})

    if search_result:
        items = search_result.find_all(attrs={'class': 'card'})
        if items:
            item = items[0]
            name = item.find(attrs={'class': 'wine-card__name'}).text.replace("\n", "")
            rate = item.find(attrs={'class': 'average__number'}).text.replace("\n", "")
            return name, rate, response.status_code
    else:
        print("[WARN] No Result")
    return '', '', response.status_code


if __name__ == "__main__":
    result = []
    with open('wine_data_from_wine21.csv', encoding='utf-8') as f:
        wine_reader = csv.reader(f)
        for row in wine_reader:
            status, name, rating = get_wine_rating(row[2])
            row.append(name)
            row.append(rating)
            row.append(status)
            result.append(row)
            print(row)
            sleep(random.randint(0, 4))

    with open('wine_data_from_wine21_vivino.csv', 'w', encoding='utf-8') as f:
        wine_writer = csv.writer(f)
        wine_writer.writerows(result)


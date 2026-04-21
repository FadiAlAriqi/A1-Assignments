import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"

def scrape_quotes():
    page = 1
    all_quotes = []

    while True:
        url = f"{BASE_URL}/page/{page}/"
        res = requests.get(url)

        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        quotes = soup.find_all("div", class_="quote")

        if not quotes:
            break

        for q in quotes:
            text = q.find("span", class_="text").text
            author = q.find("small", class_="author").text
            tags = [t.text for t in q.find_all("a", class_="tag")]

            all_quotes.append({
                "text": text,
                "author": author,
                "tags": tags
            })

        page += 1

    return all_quotes
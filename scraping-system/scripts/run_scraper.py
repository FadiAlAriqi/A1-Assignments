import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.scraper import scrape_quotes
from app.parser import clean_data
from app.storage import save_to_json

def run():
    quotes = scrape_quotes()
    cleaned = clean_data(quotes)
    save_to_json(cleaned)

if __name__ == "__main__":
    run()
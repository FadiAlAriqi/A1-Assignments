from fastapi import FastAPI
import json
from app.models import Quote

app = FastAPI()

def load_data():
    with open("data/quotes.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/quotes", response_model=list[Quote])
def get_quotes():
    return load_data()

@app.get("/quotes/author/{name}", response_model=list[Quote])
def get_by_author(name: str):
    data = load_data()
    return [
        q for q in data
        if q["author"].lower() == name.lower()
    ]
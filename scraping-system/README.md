
# Scraping System (FastAPI + Systemd + Debian Package)

## Overview
This project is a full system that demonstrates how to build a complete pipeline:

- Web scraping from an online source (https://quotes.toscrape.com)
- Data cleaning and structuring
- Saving data locally as JSON
- Exposing data via a FastAPI REST API
- Running the system as a Linux service using systemd
- Packaging the system as a Debian (.deb) package for easy deployment

---

## System Architecture

```

Scraper → Parser → Storage (JSON) → FastAPI → Client → systemd service

```

---

## Project Structure

```

scraping-system/
│
├── app/
│   ├── main.py        # FastAPI application
│   ├── scraper.py     # Web scraping logic
│   ├── parser.py      # Data cleaning
│   ├── storage.py     # Save/load JSON data
│   └── models.py     # Data models (Pydantic)
│
├── data/
│   └── quotes.json   # Stored scraped data
│
├── scripts/
│   └── run_scraper.py  # Manual scraper runner
│   └── scraping-system # CLI script (optional)
│
├── systemd/
│   └── scraper.service # systemd service file
│
├── deb/
│   └── control        # Debian package control file
│
├── requirements.txt
└── README.md

````

---

## Installation

### 1. Create virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

---

## Running the Project

### Option 1: Run API manually

```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then open:

```
http://localhost:8000/quotes
```

---

### Option 2: Run scraper manually

```
python scripts/run_scraper.py
```

---

### Option 3: Run as systemd service (production)

```
sudo systemctl daemon-reload
sudo systemctl enable scraper
sudo systemctl start scraper
```

Check status:

```
systemctl status scraper
```

---

## API Endpoints

### Get all quotes

```
GET /quotes
```

### Filter by author

```
GET /quotes/author/{name}
```

---

## Debian Package

The system can be packaged as a `.deb` file for easy deployment:

```
dpkg-deb --build scraping-system
sudo dpkg -i scraping-system.deb
```

---

## Technologies Used

* Python 3
* FastAPI
* Uvicorn
* Requests
* BeautifulSoup4
* Systemd (Linux service manager)
* Debian packaging (dpkg)

---

## Features

* Automated data scraping
* Clean structured data pipeline
* REST API access
* Background service execution
* Linux deployment ready
* Portable Debian package

---

## Author

Project built as a full system design exercise:
From script → to API → to system service → to deployable package

---

## Notes

* The system is designed for Linux (Ubuntu)
* Data is stored locally in JSON format
* Systemd ensures the API runs in background automatically

```

# Article Similarity Project

This project is designed to process a collection of articles, clean the text data, calculate the similarity between articles using **Cosine Similarity**, and provide a simple interface to find the most similar articles for a given ID.

## Project Structure

- `articles.csv`: The initial dataset containing the original articles (ID, Title, Content).
- `cleaner.py`: A module that cleans the text by converting it to lowercase and removing punctuation.
- `cleaned_articles.csv`: The output file generated after cleaning the original articles.
- `similarity_calculator.py`: A module that converts articles into numerical vectors and calculates the similarity scores.
- `similarity_data.pkl`: A binary file that stores the pre-calculated similarity results for fast access.
- `main.py`: The main entry point of the application that coordinates the entire process and provides the user interface.

---

## How to Run the Project

Follow these steps in order to process the data and use the search tool:

### Step 1: Clean the Data
Run the cleaning script to prepare the text for analysis:
```bash
python cleaner.py
```
**Why this is important:** This step ensures that the text is standardized. By converting everything to lowercase and removing punctuation, we make sure that words like "Python" and "python!" are treated as the same word, which is essential for accurate similarity calculations.

### Step 2: Calculate Similarity
Run the similarity calculator to build vectors and compare articles:
```bash
python similarity_calculator.py
```
**Why this is important:** This script creates a "Vector" for each article based on word frequency. It then performs a **Cosine Similarity** calculation between every pair of articles. The results are saved into `similarity_data.pkl` so that the search interface can retrieve them instantly without recalculating everything.

### Step 3: Run the Main Application
Finally, run the main script to interact with the system:
```bash
python main.py
```
**Why this is important:** This is the user interface. It allows you to enter an Article ID and immediately displays the **top 3 most similar articles** based on the calculations performed in the previous steps.

---

## Requirements
- Python 3.x
- `numpy` library (for vector calculations)
- `csv` and `pickle` (standard Python libraries)

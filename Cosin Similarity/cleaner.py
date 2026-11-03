import csv
import string

def clean_text(text):
    text = text.lower()
    for char in string.punctuation:
        text = text.replace(char, "")
    return text

def main():    
    with open('articles.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        articles = []
        for row in reader:
            row['Title'] = clean_text(row['Title'])
            row['Content'] = clean_text(row['Content'])
            articles.append(row)
            
    with open('cleaned_articles.csv', mode='w', encoding='utf-8', newline='') as file:
        fieldnames = ['ID', 'Title', 'Content']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(articles)
    
    print(f"The data was cleaned and saved in cleaned_articles.csv")

if __name__ == "__main__":
    main()

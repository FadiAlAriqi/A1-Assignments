import csv
import numpy as np
import pickle

def get_cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

def main():
    articles = []

    try:
        with open('cleaned_articles.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                articles.append(row)
    except FileNotFoundError:
        print("Error: cleaned_articles.csv file does not exist.")
        return
    

            
    page_of_words = []
    for article in articles:
        full_text = article['Title'] + " " + article['Content']
        words = full_text.split()
        for word in words:
            if word not in page_of_words:
                page_of_words.append(word)
                
    article_vectors = []

    for article in articles:
        full_text = article['Title'] + " " + article['Content']

        words = full_text.split()
        
        vector = []
        for word in page_of_words:
            count = words.count(word)
            vector.append(count)
        
        article_vectors.append(np.array(vector))
        
    similarity_results = {}
    for i in range(len(articles)):

        id_i = articles[i]['ID']

        similarity_results[id_i] = []
        
        for j in range(len(articles)):

            if i == j:

                continue
            
            id_j = articles[j]['ID']
            
            sim_score = get_cosine_similarity(article_vectors[i], article_vectors[j])
            
            sim_out_of_10 = round(sim_score * 10, 2)
            
            similarity_results[id_i].append({
                'ID': id_j,
                'Title': articles[j]['Title'],
                'Similarity': sim_out_of_10
            })
            
    with open('similarity_data.pkl', 'wb') as f:
        pickle.dump(similarity_results, f)
        
    print("Similarity was calculated and the results were saved in similarity_data.pkl")

if __name__ == "__main__":
    main()

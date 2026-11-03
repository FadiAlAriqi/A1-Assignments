import pickle

def main():
    try:
        with open('similarity_data.pkl', 'rb') as f:
            similarity_results = pickle.load(f)
    except FileNotFoundError:
        print("Error: similarity_data.pkl file does not exist. Please run similarity_calculator.py first.")
        return

    print("\n--- System for finding similar articles ---\n")
    print(f"Available articles (ID): {', '.join(similarity_results.keys())}\n")
    
    user_input = input("Enter the ID of the article to find 3 most similar articles: ")
    
    if user_input in similarity_results:
        similar_articles = sorted(similarity_results[user_input], key=lambda x: x['Similarity'], reverse=True)
        
        print(f"\nTop 3 articles similar to article number {user_input}:")
        for i in range(min(3, len(similar_articles))):
            article = similar_articles[i]
            print(f"{i+1}. Article ID {article['ID']} - Title: {article['Title']} - Similarity: {article['Similarity']} out of 10")
    else:
        print("Sorry, the article ID does not exist.")

if __name__ == "__main__":
    main()

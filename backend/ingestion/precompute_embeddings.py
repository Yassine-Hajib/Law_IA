import json
import os
from sentence_transformers import SentenceTransformer

def main():
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    input_path = os.path.join(os.path.dirname(__file__), "../data/json/structred_Law_Article.json")
    output_path = os.path.join(os.path.dirname(__file__), "../data/json/precomputed_embeddings.json")

    print(f"Loading data from {input_path}...")
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    embeddings_data = []

    print("Computing embeddings...")
    for i, item in enumerate(data):
        article_id = item.get("article_id")
        text = item.get("text")
        
        if not article_id or not text:
            continue
            
        embedding = model.encode(text).tolist()
        
        embeddings_data.append({
            "id": article_id,
            "text": text,
            "embedding": embedding
        })
        
        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1} articles...")

    print(f"Saving {len(embeddings_data)} embeddings to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(embeddings_data, f, ensure_ascii=False)
        
    print("Done! You can now use precomputed_embeddings.json for lightweight Vercel deployment.")

if __name__ == "__main__":
    main()

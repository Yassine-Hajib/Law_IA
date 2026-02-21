import json
from sentence_transformers import SentenceTransformer
import chromadb

# Load model
model = SentenceTransformer("BAAI/bge-small-en")

# Load JSON
with open("../../Data/json/structred_Law_Article.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Persistent database
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="law_articles")

for item in data:
    # Make sure the keys exist
    article_id = item.get("article_id")
    text = item.get("text")
    if not article_id or not text:
        continue  # skip invalid entries

    # Encode the text
    embedding = model.encode(text).tolist()

    # Add to ChromaDB
    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[article_id]
    )

print("Embeddings stored in chroma_db folder!")
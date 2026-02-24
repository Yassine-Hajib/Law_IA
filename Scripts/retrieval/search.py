import chromadb
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer("BAAI/bge-small-en")

# Load ChromaDB
client = chromadb.PersistentClient(path="../embeeding/chroma_db")
collection = client.get_collection("law_articles")

query = "j'ai perdu mon travail , qu'est ce que je dois faire ? "

# Convert question to embedding
query_embedding = model.encode(query).tolist()

# Search
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print(results["documents"])
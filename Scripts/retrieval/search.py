import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder

# ---------------------------
# Load embedding model
# ---------------------------
model = SentenceTransformer("BAAI/bge-small-en")

# ---------------------------
# Load ChromaDB
# ---------------------------
client = chromadb.PersistentClient(path="../embeeding/chroma_db")
collection = client.get_collection("law_articles")


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

# ---------------------------
# User query
# ---------------------------
query = "licenciement et droits du salarié après rupture du contrat"
query = query.strip().lower()

# ---------------------------
# Convert question to embedding
# ---------------------------
query_embedding = model.encode(query).tolist()

# ---------------------------
# Retrieve Top 5 documents
# ---------------------------
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=8
)

documents = results["documents"][0]

print("\nTop documents from Chroma:\n")
for doc in documents:
    print("-", doc[:150], "...\n")

# ---------------------------
# Re-ranking with Cross-Encoder
# ---------------------------
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

pairs = [(query, doc) for doc in documents]
scores = cross_encoder.predict(pairs)

ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)

print("\nTop article after re-ranking:\n")
print(ranked[0][0])
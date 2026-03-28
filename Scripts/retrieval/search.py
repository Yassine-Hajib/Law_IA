import chromadb
import requests
from sentence_transformers import SentenceTransformer, CrossEncoder


# Load embedding model (Bi-Encoder)

model = SentenceTransformer("BAAI/bge-small-en")

    # Connecting To The DataBase 
client = chromadb.PersistentClient(path="../embeeding/chroma_db")
collection = client.get_collection("law_articles")

query = "licenciement et droits du salarié après rupture du contrat"
query = query.strip().lower()

    # If The Question is to short 
if len(query.split()) < 5:
    query = f"droits du salarié en droit du travail marocain concernant : {query}"

    # Converts the question into a vector 
query_embedding = model.encode(query).tolist()

    # Top 8 vector  in chroma related to the question 
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5   # reduced for speed
)

documents = results["documents"][0]

print("\n Top documents from Chroma:\n")
for doc in documents:
    print("-", doc[:150], "...\n")


# Re-ranking with Cross-Encoder

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
pairs = [(query, doc) for doc in documents]
scores = cross_encoder.predict(pairs)
ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)

# Keep top 3 after reranking

top_docs = [doc for doc, score in ranked[:3]]


# Build context

context = "\n\n".join(
    [f"Article {i+1}:\n{doc}" for i, doc in enumerate(top_docs)]
)


# Build optimized prompt

prompt = f"""
Tu es un assistant juridique spécialisé en droit du travail marocain.

Instructions strictes:
- Organise la réponse en sections claires.
- Utilise une numérotation correcte (1, 2, 3).
- Ne répète aucune information.
- Cite les articles explicitement.
- Utilise uniquement les informations du contexte.
- Si l'information n'existe pas dans le contexte, réponds uniquement:
"Non précisé dans les articles fournis."
- Ne répète jamais que l'information est précisée.
- Ne reformule pas les instructions.

Contexte:
{context}

Question:
{query}

Réponse structurée:
"""


# Call Ollama (FAST VERSION)

print("\nGénération rapide avec Mistral...\n")

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "mistral:7b-instruct-q4_K_M",   # faster model
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 450,     # limit output length
            "temperature": 0.1 ,
            "top_p": 0.9   # more factual
        }
    }
)

result = response.json()

print("\nRéponse finale:\n")
print(result["response"])
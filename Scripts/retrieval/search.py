import chromadb
import requests
from sentence_transformers import SentenceTransformer, CrossEncoder


model = SentenceTransformer("BAAI/bge-small-en")


client = chromadb.PersistentClient(path="../embeeding/chroma_db")
collection = client.get_collection("law_articles")


query = "licenciement et droits du salarié après rupture du contrat"
query = query.strip().lower()


if len(query.split()) < 5:
    query = f"droits du salarié en droit du travail marocain concernant : {query}"


query_embedding = model.encode(query).tolist()


results = collection.query(
    query_embeddings=[query_embedding],
    n_results=8
)

documents = results["documents"][0]

print("\nTop documents from Chroma:\n")
for doc in documents:
    print("-", doc[:150], "...\n")


# Re-ranking with Cross-Encoder

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

pairs = [(query, doc) for doc in documents]
scores = cross_encoder.predict(pairs)

ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)

# Keep top 3 after reranking
top_docs = [doc for doc, score in ranked[:3]]


context = "\n\n".join(
    [f"Article {i+1}:\n{doc}" for i, doc in enumerate(top_docs)]
)


prompt = f"""
Tu es un assistant juridique spécialisé en droit du travail marocain.

Règles importantes :
- Réponds uniquement en utilisant les informations fournies dans le contexte.
- Ne rajoute aucune information externe.
- Cite les articles mentionnés si possible.
- Structure la réponse clairement.
- Si l'information n'existe pas dans le contexte, dis : "Cette information n'est pas précisée dans les articles fournis."

Contexte juridique :
{context}

Question :
{query}

Réponse détaillée :
"""


# Call Ollama (Mistral)

print("\n Génération de la réponse par Mistral...\n")

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }
)

result = response.json()

print("\nRéponse finale générée par le LLM:\n")
print(result["response"])
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import requests
from sentence_transformers import SentenceTransformer, CrossEncoder
import os
import re
import torch
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = "mps" if torch.backends.mps.is_available() else "cpu"
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device=device)

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "..", "chroma_db")
client = chromadb.PersistentClient(path=db_path)
collection = client.get_collection("law_articles")

def extract_article_number(text):
    match = re.search(r"article\s*(\d+)", text.lower())
    return match.group(1) if match else "unknown"

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
def chat(payload: ChatRequest):
    query = payload.query
    query_processed = query.strip().lower()

    if not query_processed or len(re.findall(r"[a-zA-ZÀ-ÿ]", query_processed)) < 3:
        return {"response": "Question trop courte ou invalide.", "sources": []}

    # Better query expansion
    if len(query_processed.split()) < 5:
        query_processed = f"droit du travail marocain responsabilités conditions légales article : {query_processed}"

    try:
        query_embedding = model.encode(query_processed).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5  # No reranking needed for a good model
        )
        documents = results["documents"][0]
        ids = results["ids"][0]

        context_parts = []
        for doc_id, doc in zip(ids, documents):
            context_parts.append(f"{doc_id} :\n{doc}")

        context = "\\n\\n".join(context_parts)
        top_docs = context_parts

    except Exception as e:
        return {"response": f"Erreur de recherche (RAG) : {e}", "sources": []}

    system_prompt = """Tu es un expert du droit du travail marocain.

RÈGLES D'INTERPRÉTATION (TRÈS IMPORTANT) :
Si l'utilisateur emploie des termes familiers (ex: "vacances pour la femme enceinte"), tu DOIS répondre directement avec les règles du "congé de maternité" (14 semaines). Ne lui dis SURTOUT PAS que "la loi ne parle pas de vacances mais de congé". Réponds directement à son intention !

RÈGLES DE FORMATAGE STRICTES (Très professionnel, SANS EMOJI) :
Structure ta réponse OBLIGATOIREMENT comme ceci (avec des sauts de ligne) :

**Réponse :** [Donne la réponse factuelle directement]

**Explication :** [Résumé simple de la règle juridique en 1 ou 2 phrases]

**Base Légale :** [Numéro de l'Article exact, ex: Article 154]

INTERDICTIONS :
- NE JAMAIS utiliser d'emojis.
- Ne jamais dire "Bonjour" ou d'autres phrases de politesse.
- Ne réponds "Non précisé" que si le sujet général n'existe vraiment pas dans le contexte.
"""

    user_prompt = f"Contexte juridique :\\n{context}\\n\\nQuestion :\\n{query}\\n"

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not GROQ_API_KEY:
         return {"response": "Erreur : Clé API Groq manquante dans .env.", "sources": []}

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1
            },
            timeout=60
        )

        if response.status_code != 200:
             return {"response": f"Erreur API Groq ({response.status_code}) : {response.text}", "sources": []}

        data = response.json()
        full_response = data["choices"][0]["message"]["content"]

        return {
            "response": full_response,
            "sources": top_docs
        }

    except Exception as e:
        return {"response": f"Erreur de génération : {e}", "sources": []}

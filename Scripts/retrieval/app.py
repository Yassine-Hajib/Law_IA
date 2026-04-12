import streamlit as st
import chromadb
import requests
from sentence_transformers import SentenceTransformer, CrossEncoder
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Assistant Juridique",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ Assistant Juridique - Droit du Travail Marocain")
st.markdown("Posez vos questions sur le Code du Travail marocain, et je vous répondrai en me basant sur les textes de loi.")

@st.cache_resource
def load_models():
    """Charge les modèles (SentenceTransformer et CrossEncoder)."""
    import torch
    
    # Utilisation de l'accélération matérielle Apple Silicon (MPS) si disponible
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    
    model = SentenceTransformer("BAAI/bge-small-en", device=device)
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=device)
    return model, cross_encoder

@st.cache_resource
def load_db():
    """Charge la base de données vectorielle ChromaDB."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "embeeding", "chroma_db")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection("law_articles")
    return collection

# Chargement en cache
try:
    with st.spinner("Chargement des modèles en cours..."):
        model, cross_encoder = load_models()
        collection = load_db()
except Exception as e:
    st.error(f"Erreur lors du chargement des modèles ou de la base de données : {e}")
    st.stop()

# Zone de saisie utilisateur
query = st.text_input("Votre question :", placeholder="Ex: Quels sont mes droits en cas de licenciement abusif ?")

# Groq API config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if st.button("Rechercher") and query:
    query_processed = query.strip().lower()

    # Filtre minimal côté application: ne bloque que les entrées vides/bruit évident.
    if not query_processed:
        st.warning("Veuillez poser une question claire et pertinente en rapport avec le droit du travail marocain.")
        st.stop()
    alpha_count = len(re.findall(r"[a-zA-ZÀ-ÿ]", query_processed))
    if alpha_count < 3:
        st.warning("Veuillez poser une question claire et pertinente en rapport avec le droit du travail marocain.")
        st.stop()
    
    # Amélioration de la requête si elle est trop courte
    if len(query_processed.split()) < 5:
        query_processed = f"droits du salarié en droit du travail marocain concernant : {query_processed}"

    with st.spinner("Recherche dans le Code du Travail..."):
        try:
            # 1. Retrieval
            query_embedding = model.encode(query_processed).tolist()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=8
            )
            documents = results["documents"][0]
            
            # 2. Reranking
            pairs = [(query_processed, doc) for doc in documents]
            scores = cross_encoder.predict(pairs)
            
            # Trier par score décroissant
            ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
            
            # Garder les 3 documents les plus pertinents
            top_docs = [doc for doc, score in ranked[:3]]
            
            context = "\n\n".join(
                [f"Article {i+1}:\n{doc}" for i, doc in enumerate(top_docs)]
            )
            
            # Préparation du prompt pour le LLM
            system_prompt = """Tu es un assistant juridique strict et professionnel, expert en droit du travail marocain.
Réponds en te basant EXCLUSIVEMENT sur le contexte juridique fourni.

RÈGLES OBLIGATOIRES :
1. Ne fais AUCUNE classification d'intention (hors sujet, salutations, etc.) : réponds juridiquement à la question posée en utilisant le contexte.
2. Si le contexte ne contient pas l'information nécessaire, réponds UNIQUEMENT :
"Cette information n'est pas précisée dans les textes de loi fournis."
3. Si le contexte contient la réponse, fournis une réponse claire, structurée, concise, et cite explicitement les articles utilisés.
4. N'invente jamais d'article ni de règle absente du contexte."""

            user_prompt = f"""Contexte juridique (Ne réponds qu'à partir de ceci) :
{context}

Question de l'utilisateur :
{query}"""
            
        except Exception as e:
            st.error(f"Erreur lors de la recherche dans la base de données : {e}")
            st.stop()
            
    with st.spinner("Génération de la réponse par l'IA..."):
        try:
            # 3. Génération via Groq API
            if not GROQ_API_KEY:
                st.error("Clé API Groq manquante. Définissez `GROQ_API_KEY` dans votre environnement avant de lancer l'application.")
                st.stop()

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
                    "temperature": 0.1,
                    "stream": False
                },
                timeout=60
            )

            if response.status_code != 200:
                st.error(f"Erreur de l'API Groq (Code {response.status_code})")
                st.write(response.text)
                st.stop()

            data = response.json()
            full_response = data["choices"][0]["message"]["content"]
            st.success("Réponse générée :")
            st.markdown(full_response)

            # Affichage des sources utilisées
            with st.expander("Voir les articles de loi utilisés (Sources)"):
                for i, doc in enumerate(top_docs):
                    st.markdown(f"**Source {i+1} :**")
                    st.info(doc)

        except requests.exceptions.ConnectionError:
            st.error("Impossible de se connecter à Groq. Vérifiez votre connexion Internet et la validité de `GROQ_API_KEY`.")
        except Exception as e:
            st.error(f"Erreur lors de la génération : {e}")
     
import streamlit as st
import chromadb
import requests
from sentence_transformers import SentenceTransformer, CrossEncoder
import os
import re
from dotenv import load_dotenv

load_dotenv()

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Assistant Juridique",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ Assistant Juridique - Droit du Travail Marocain")
st.markdown("Posez vos questions sur le Code du Travail marocain.")

# ------------------ LOAD MODELS ------------------
@st.cache_resource
def load_models():
    import torch
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    
    model = SentenceTransformer("BAAI/bge-small-en", device=device)
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=device)
    
    return model, cross_encoder

# ------------------ LOAD DB ------------------
@st.cache_resource
def load_db():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "embeeding", "chroma_db")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection("law_articles")
    return collection

# ------------------ HELPERS ------------------
def extract_article_number(text):
    match = re.search(r"article\s*(\d+)", text.lower())
    return match.group(1) if match else "unknown"

# ------------------ INIT ------------------
try:
    with st.spinner("Chargement des modèles..."):
        model, cross_encoder = load_models()
        collection = load_db()
except Exception as e:
    st.error(f"Erreur chargement : {e}")
    st.stop()

# ------------------ INPUT ------------------
query = st.text_input("Votre question :", placeholder="Ex: droits en cas de licenciement abusif")

# ------------------ API CONFIG ------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# ------------------ MAIN ------------------
if st.button("Rechercher") and query:
    query_processed = query.strip().lower()

    # Basic cleaning
    if not query_processed:
        st.warning("Question invalide.")
        st.stop()

    alpha_count = len(re.findall(r"[a-zA-ZÀ-ÿ]", query_processed))
    if alpha_count < 3:
        st.warning("Question trop courte.")
        st.stop()

    # 🔥 Better query expansion
    if len(query_processed.split()) < 5:
        query_processed = f"droit du travail marocain responsabilités conditions légales article : {query_processed}"

    # ------------------ RETRIEVAL ------------------
    with st.spinner("Recherche..."):
        try:
            query_embedding = model.encode(query_processed).tolist()

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=12  # 🔥 more context
            )

            documents = results["documents"][0]

            # ------------------ RERANK ------------------
            pairs = [(query_processed, doc) for doc in documents]
            scores = cross_encoder.predict(pairs)

            ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)

            # 🔥 keep more docs
            top_docs = [doc for doc, score in ranked[:6]]

            # ------------------ MERGE ARTICLES ------------------
            grouped_articles = {}

            for doc in top_docs:
                article_num = extract_article_number(doc)
                grouped_articles.setdefault(article_num, []).append(doc)

            context = "\n\n".join([
                f"Article {num}:\n" + " ".join(parts)
                for num, parts in grouped_articles.items()
            ])

        except Exception as e:
            st.error(f"Erreur recherche : {e}")
            st.stop()

    # ------------------ PROMPT ------------------
    system_prompt = """Tu es un assistant juridique expert en droit du travail marocain.

RÈGLES STRICTES :

1. Analyse TOUT le contexte fourni sans ignorer aucune partie.
2. Si plusieurs conditions ou cas existent, tu dois TOUS les expliquer.
3. Ne donne JAMAIS une réponse partielle.
4. Cite explicitement les articles utilisés.
5. Si info absente du contexte, répond UNIQUEMENT :
"Cette information n'est pas précisée dans les textes de loi fournis."
6. N'invente jamais d'information.

OBJECTIF :
Donner une réponse complète, claire et fidèle au texte."""

    user_prompt = f"""
Contexte juridique :
{context}

Question :
{query}
"""

    # ------------------ GENERATION ------------------
    with st.spinner("Génération..."):
        try:
            if not GROQ_API_KEY:
                st.error("Clé API manquante.")
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
                    "temperature": 0.1
                },
                timeout=60
            )

            if response.status_code != 200:
                st.error(f"Erreur API {response.status_code}")
                st.write(response.text)
                st.stop()

            data = response.json()
            full_response = data["choices"][0]["message"]["content"]

            st.success("Réponse :")
            st.markdown(full_response)

            # ------------------ SOURCES ------------------
            with st.expander("Sources utilisées"):
                for i, doc in enumerate(top_docs):
                    st.markdown(f"**Source {i+1} :**")
                    st.info(doc)

        except Exception as e:
            st.error(f"Erreur génération : {e}")
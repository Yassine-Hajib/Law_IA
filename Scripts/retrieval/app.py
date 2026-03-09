import streamlit as st
import chromadb
import requests
from sentence_transformers import SentenceTransformer, CrossEncoder

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
    model = SentenceTransformer("BAAI/bge-small-en")
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return model, cross_encoder

import os

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

if st.button("Rechercher") and query:
    query_processed = query.strip().lower()
    
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
            prompt = f"""
            Tu es un assistant juridique spécialisé en droit du travail marocain.
            
            Règles importantes :
            - Si la Question est une suite de lettres sans signification (ex: 'jkzkjfndzjkldlz', 'jdejdhe') ou n'a aucun sens, tu DOIS répondre UNIQUEMENT par : "Veuillez poser une question claire et pertinente." et ignorer le reste.
            - Sinon, réponds uniquement en utilisant les informations fournies dans le contexte.
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
            
        except Exception as e:
            st.error(f"Erreur lors de la recherche dans la base de données : {e}")
            st.stop()
            
    with st.spinner("Génération de la réponse par l'IA..."):
        try:
            # 3. Génération (Mistral via Ollama)
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success("Réponse prête :")
                st.write(result["response"])
                
                # Affichage des sources seulement si la question est pertinente
                if "Veuillez poser une question claire" not in result["response"]:
                    with st.expander("Voir les articles de loi utilisés (Sources)"):
                        for i, doc in enumerate(top_docs):
                            st.markdown(f"**Source {i+1} :**")
                            st.info(doc)
            else:
                st.error(f"Erreur de l'API Ollama (Code {response.status_code})")
                st.write(response.text)
                
        except requests.exceptions.ConnectionError:
            st.error("Impossible de se connecter à Ollama. Veuillez vérifier que Ollama est bien lancé (ex: `ollama run mistral` ou `ollama serve`).")
        except Exception as e:
            st.error(f"Erreur lors de la génération : {e}")

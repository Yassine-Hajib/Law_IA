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
    import torch
    
    # Utilisation de l'accélération matérielle Apple Silicon (MPS) si disponible
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    
    model = SentenceTransformer("BAAI/bge-small-en", device=device)
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=device)
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
            system_prompt = """Tu es un assistant juridique strict et professionnel, expert en droit du travail marocain.
Ton SEUL ET UNIQUE but est de répondre aux questions sur le droit du travail marocain en utilisant EXCLUSIVEMENT le contexte fourni.

RÈGLES STRICTES ET OBLIGATOIRES (Ne les enfreins sous aucun prétexte) :
1. Si la question n'a AUCUN rapport avec le droit du travail (ex: "bonjour", "comment ça va", "quel est ton nom", "je m'appelle X", "qui est le président"), tu DOIS répondre EXACTEMENT et UNIQUEMENT : "Veuillez poser une question claire et pertinente en rapport avec le droit du travail marocain." Ne dis rien d'autre.
2. Si la question est une suite de lettres incompréhensible ou du bruit (ex: "jkzkjf", "93022", "hjkjjkdf"), tu DOIS répondre EXACTEMENT et UNIQUEMENT : "Veuillez poser une question claire et pertinente en rapport avec le droit du travail marocain."
3. Ne réponds JAMAIS aux questions hors sujet, même pour être poli.
4. Si la question est pertinente au droit du travail mais que le contexte fourni ne contient pas la réponse, réponds UNIQUEMENT : "Cette information n'est pas précisée dans les textes de loi fournis."
5. Si la réponse est dans le contexte, donne une réponse claire, complète et cite toujours les articles mentionnés."""

            user_prompt = f"""Contexte juridique (Ne réponds qu'à partir de ceci) :
{context}

Question de l'utilisateur :
{query}"""
            
        except Exception as e:
            st.error(f"Erreur lors de la recherche dans la base de données : {e}")
            st.stop()
            
    with st.spinner("Génération de la réponse par l'IA..."):
        try:
            # 3. Génération (LLama 3 via Ollama API Chat)
            import json
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3.2:1b",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": True # On garde le streaming pour la vitesse
                },
                stream=True
            )
            
            if response.status_code == 200:
                st.success("Génération de la réponse en cours :")
                response_placeholder = st.empty()
                full_response = ""
                
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            full_response += chunk["message"]["content"]
                            response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                
                # Affichage des sources seulement si la question est pertinente
                if "Veuillez poser une question claire" not in full_response:
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

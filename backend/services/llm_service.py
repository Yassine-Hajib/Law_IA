import requests
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.models import BaseDesLois, Message
from backend.core.config import settings

def call_ollama(prompt: str) -> str:
    """Appelle l'API Ollama locale avec le modèle Mistral"""
    try:
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erreur avec l'IA: {str(e)}")

def process_law_question(db: Session, question: str, session_id: int):
    """
    Logique métier de l'Étape 3 : 
    1. Prendre la question.
    2. (Bouchonné pour l'instant) Chercher dans la base des lois (ChromaDB dans votre app Streamlit).
    3. Formater le Prompt.
    4. Appeler Mistral.
    5. Sauvegarder dans la DB.
    """
    # 1. Optionnel : Effectuer une recherche dans ChromaDB ici si vous l'intégrez au Backend
    # Pour l'instant, on suppose que la recherche vectorielle retourne ce contexte :
    contexte_juridique = "Le Code du travail marocain stipule que la période d'essai pour les CDI est de..."
    
    # 2. Formater le Prompt
    prompt = f"Tu es un assistant juridique expert en droit marocain. \nContexte: {contexte_juridique}\n\nQuestion: {question}\nRéponse:"
    
    # 3. Appeler Mistral
    reponse_ia = call_ollama(prompt)
    
    # 4. Sauvegarder la question (User)
    msg_user = Message(contenu=question, expediteur="User", session_id=session_id)
    db.add(msg_user)
    
    # 5. Sauvegarder la réponse (IA)
    msg_ia = Message(contenu=reponse_ia, expediteur="IA", session_id=session_id)
    db.add(msg_ia)
    
    db.commit()
    db.refresh(msg_ia)
    
    return msg_ia

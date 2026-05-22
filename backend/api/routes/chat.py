from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.core.database import get_db
from backend.schemas.schemas import SessionChatCreate, SessionChatOut, MessageCreate, MessageOut
from backend.models.models import Utilisateur
from backend.api.deps import get_current_user
from backend.services.chat_service import create_chat_session, get_user_chat_sessions, get_session_by_id
from backend.services.llm_service import process_law_question

router = APIRouter()

@router.post("/sessions", response_model=SessionChatOut)
def create_session(
    session_data: SessionChatCreate, 
    db: Session = Depends(get_db), 
    current_user: Utilisateur = Depends(get_current_user)
):
    """Créer une nouvelle session de chat pour l'utilisateur connecté"""
    return create_chat_session(db, session_data, current_user)

@router.get("/sessions", response_model=List[SessionChatOut])
def list_sessions(
    db: Session = Depends(get_db), 
    current_user: Utilisateur = Depends(get_current_user)
):
    """Récupérer tout l'historique (toutes les sessions) d'un utilisateur spécifique"""
    return get_user_chat_sessions(db, current_user)

@router.post("/sessions/{session_id}/message", response_model=MessageOut)
def post_message(
    session_id: int, 
    msg: MessageCreate, 
    db: Session = Depends(get_db), 
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Envoyer un message à l'IA.
    Prend la question, cherche dans la base de loi, et renvoie la réponse de Mistral.
    """
    # 1. Vérifier que la session appartient bien à l'utilisateur
    get_session_by_id(db, session_id, current_user)
    
    # 2. Traiter la requête (Base des Lois + LLM)
    return process_law_question(db, msg.contenu, session_id)

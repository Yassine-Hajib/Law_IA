from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.models.models import SessionChat, Utilisateur
from backend.schemas.schemas import SessionChatCreate

def create_chat_session(db: Session, session_data: SessionChatCreate, current_user: Utilisateur) -> SessionChat:
    new_session = SessionChat(
        titre=session_data.titre,
        utilisateur_id=current_user.id
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def get_user_chat_sessions(db: Session, current_user: Utilisateur):
    # Récupérer toutes les sessions de l'utilisateur connecté
    return db.query(SessionChat).filter(SessionChat.utilisateur_id == current_user.id).all()

def get_session_by_id(db: Session, session_id: int, current_user: Utilisateur) -> SessionChat:
    # Récupérer la session
    session = db.query(SessionChat).filter(SessionChat.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
        
    # Vérifier que la session appartient bien à l'utilisateur
    if session.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à cette session")
        
    return session

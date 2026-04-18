from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.schemas.schemas import UtilisateurCreate, UtilisateurOut, UtilisateurLogin, Token
from backend.services.auth_service import register_user, authenticate_user

router = APIRouter()

@router.post("/register", response_model=UtilisateurOut)
def register(user_data: UtilisateurCreate, db: Session = Depends(get_db)):
    """Inscrire un nouvel utilisateur"""
    return register_user(db, user_data)

@router.post("/login", response_model=Token)
def login(user_data: UtilisateurLogin, db: Session = Depends(get_db)):
    """Se connecter et obtenir un JWT"""
    return authenticate_user(db, user_data)

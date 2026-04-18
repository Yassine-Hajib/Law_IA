from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.models.models import Utilisateur
from backend.schemas.schemas import UtilisateurCreate, UtilisateurLogin, Token
from backend.core.security import get_password_hash, verify_password, create_access_token

def register_user(db: Session, user_data: UtilisateurCreate) -> Utilisateur:
    # 1. Vérifier si l'email existe déjà
    db_user = db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # 2. Hacher le mot de passe
    hashed_password = get_password_hash(user_data.mot_de_passe)
    
    # 3. Créer le nouvel utilisateur
    new_user = Utilisateur(
        nom=user_data.nom,
        email=user_data.email,
        mot_de_passe=hashed_password
    )
    
    # 4. Sauvegarder dans la DB
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def authenticate_user(db: Session, user_data: UtilisateurLogin) -> Token:
    # 1. Chercher l'utilisateur par e-mail
    user = db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first()
    
    # 2. Vérifier si l'utilisateur existe et si le mot de passe correspond
    if not user or not verify_password(user_data.mot_de_passe, user.mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Générer le token JWT
    access_token = create_access_token(data={"sub": user.email})
    
    return Token(access_token=access_token, token_type="bearer")

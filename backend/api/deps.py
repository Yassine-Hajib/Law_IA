from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.config import settings
from backend.models.models import Utilisateur
from backend.schemas.schemas import TokenData

# Ce composant indique à FastAPI que les routes protégées nécessitent un token JWT dans l'en-tête Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Utilisateur:
    """
    Middleware/Décorateur qui vérifie le token JWT et retourne l'utilisateur connecté.
    Si le token est invalide, une erreur 401 est levée.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Décodage du token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    # Recherche de l'utilisateur dans la base de données
    user = db.query(Utilisateur).filter(Utilisateur.email == token_data.email).first()
    if user is None:
        raise credentials_exception
        
    return user

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import auth, chat
from backend.core.database import engine, Base
from backend.core.config import settings

# Création des tables dans la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API FastAPI pour l'application d'assistant juridique Law_IA",
    version="1.0.0"
)

# Configuration CORS pour autoriser Streamlit (par défaut sur 8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"], # Changer en ["*"] en développement si besoin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat & IA"])

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de Law_IA"}

from fastapi import APIRouter, Depends

from app.config import get_settings
from app.db import mongo, neo4j_db
from app.deps import get_current_user
from app.models import User
from app.services.ollama import ollama_service

router = APIRouter(prefix="/api", tags=["system"])
settings = get_settings()


@router.get("/health")
def health():
    ollama_ok = ollama_service.ping()
    return {
        "ok": True,
        "postgres": "configured",
        "mongo": mongo.mongo_mode,
        "neo4j": neo4j_db.graph_mode,
        "ollama": ollama_ok,
        "ollama_model": settings.ollama_model,
        "display_threshold": settings.display_threshold,
        "score_weights": {
            "eligibility": settings.eligibility_weight,
            "document": settings.document_weight,
        },
    }


@router.get("/preferences/languages")
def languages(_: User = Depends(get_current_user)):
    return {
        "supported_ui": ["en", "hi", "mni"],
        "fallback": "en",
        "user_language_is_sent_to_ai": True,
    }

# routers/chat.py - Version FINALE corrigée

from fastapi import APIRouter, Body, HTTPException
from fastapi.concurrency import run_in_threadpool
from dependencies import get_llm, get_rag_context
import logging

router = APIRouter(prefix="/chat", tags=["Chatbot"])

logger = logging.getLogger(__name__)

@router.post("/")
async def chat(payload: dict = Body(...)):
    """
    Endpoint chatbot : accepte {"query": "votre question"}
    Renvoie TOUJOURS {"response": "..."} pour compatibilité dashboard
    """
    query = payload.get("query", "")
    
    if not query.strip():
        logger.warning("Requête vide reçue")
        return {"response": "Pose-moi une vraie question sur ta base Oracle ! 😊"}

    try:
        logger.info(f"Requête reçue : {query[:100]}...")

        # Récupération du contexte RAG
        context = get_rag_context(query)
        
        # Génération avec Gemini (Exécuté dans un thread séparé)
        response_text = await run_in_threadpool(
            get_llm().generate,
            prompt=query,
            context=context,
            user_context="Tu es un expert DBA Oracle. Réponds en français, clair, structuré et professionnel."
        )
        
        logger.info(f"Réponse générée ({len(response_text)} caractères)")
        return {"response": response_text.strip()}
    
    except Exception as e:
        error_msg = f"Erreur génération : {str(e)}"
        logger.error(error_msg)
        return {"response": f"Désolé, une erreur est survenue : {error_msg}. Réessayez ou contactez le support."}
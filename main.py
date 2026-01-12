# backend/main.py - Version finale FastAPI

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.concurrency import run_in_threadpool
from routers import security, performance, anomaly, backup, chat, utils
from dependencies import set_llm
from src.data_extractor import extract_data
from src.llm_engine import LLMEngine

app = FastAPI(
    title="Plateforme Intelligente Oracle avec IA - API",
    description="Backend FastAPI pour le projet DBA 2026",
    version="1.0"
)

# ========================
# CORS - Autorise Streamlit (localhost:8501) et tout en dev
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod, remplace par ["http://localhost:8501"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Inclusion des routers
# ========================
app.include_router(security.router)
app.include_router(performance.router)
app.include_router(anomaly.router)
app.include_router(backup.router)
app.include_router(chat.router)
app.include_router(utils.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <h1>🌟 Plateforme Intelligente Oracle avec IA</h1>
    <p>API FastAPI en marche !</p>
    <p><a href="/docs">Documentation Swagger</a></p>
    <p>Dashboard Streamlit : <a href="http://localhost:8501" target="_blank">http://localhost:8501</a></p>
    """

@app.post("/connect-and-refresh")
async def connect_and_refresh(config: dict = Body(...)):
    """
    Reçoit la config Oracle + choix LLM de l'utilisateur
    Extrait les données de SA base et configure le LLM
    """
    try:
        # Extraction des données avec la config utilisateur (Exécuté dans un thread séparé)
        message = await run_in_threadpool(extract_data, config)
        
        # Configuration du LLM selon le choix utilisateur
        provider = config.get("llm_provider", "groq")
        gemini_key = config.get("gemini_api_key", None)
        
        new_llm = LLMEngine(
            provider=provider,
            gemini_api_key=gemini_key if provider == "gemini" else None,
            ollama_model="phi3:mini"
        )
        
        # Mise à jour de l'instance globale partagée
        set_llm(new_llm)
        
        print(f"LLM configuré : {provider.upper()}")
        
        return {
            "message": f"{message} | LLM : {provider.upper()} configuré",
            "status": "success"
        }
        
    except Exception as e:
        return {
            "message": f"Erreur : {str(e)}",
            "status": "error"
        }

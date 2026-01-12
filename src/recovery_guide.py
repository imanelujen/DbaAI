# backend/src/recovery_guide.py - Version accélérée et personnalisée

from src.llm_engine import LLMEngine
from src.rag_setup import retrieve_context
import time

engine = LLMEngine()

def guide_recovery(scenario, details):
    start = time.time()
    # Personnalisation : stats base
    user_context = "Base utilisateur avec archive logs activés, RMAN configuré, 5 PDB. Détecte si changement depuis dernière backup."

    # RAG réduit
    context = "\n".join(retrieve_context(f"oracle recovery {scenario} rman flashback", top_k=3))

    playbook = engine.generate(
        f"Guide DBA étape par étape pour {scenario} en français. Détails : {details}. Inclure commandes RMAN/SQL.",
        context=context,
        user_context=user_context
    )

    print(f"Guide généré en {time.time() - start}s")
    return playbook.strip()
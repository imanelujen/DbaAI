import json
from dependencies import get_llm
from src.rag_setup import retrieve_context
import time
import logging
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

async def detect_anomalies(log_file="data/synthetic_logs.json"):
    start = time.time()
    results = []
    stats = {"precision": 0.0, "recall": 0.0, "total_logs": 0, "errors": 0}

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
        stats["total_logs"] = len(logs)
    except Exception as e:
        logger.error(f"Impossible de lire {log_file} : {e}")
        return [], stats

    if not logs:
        return [], stats

    # Limite pour éviter de saturer le context window
    max_logs = 10 
    logs_to_analyze = logs[:max_logs]
    
    # Batching : On envoie tout d'un coup
    logs_block = json.dumps(logs_to_analyze, indent=2, ensure_ascii=False)
    
    user_context = f"Base avec {len(logs)} logs. Focus DBA : Injection SQL, Escalade privilèges, Accès hors heures."
    context = "\n".join(retrieve_context("oracle audit anomaly sql injection", top_k=2))

    prompt = (
        f"Analyse ces {len(logs_to_analyze)} logs d'audit Oracle ci-dessous.\n"
        f"Pour CHAQUE log, détermine s'il est 'normal', 'suspect' ou 'critique'.\n"
        f"LOGS :\n{logs_block}\n\n"
        f"REPONDS UNIQUEMENT avec un tableau JSON de la forme :\n"
        f"[{{'log_index': 0, 'classification': 'critique', 'justification': '...'}}, ...]"
    )

    try:
        response_text = await run_in_threadpool(
            get_llm().generate,
            prompt,
            context=context,
            user_context=user_context
        )
        
        # Nettoyage JSON
        cleaned_json = response_text.replace("```json", "").replace("```", "").strip()
        analysis_results = json.loads(cleaned_json)
        
        # Fusion avec les logs originaux
        for res in analysis_results:
            idx = res.get("log_index")
            if idx is not None and 0 <= idx < len(logs_to_analyze):
                results.append({
                    "log": logs_to_analyze[idx],
                    "classification": res.get("classification", "inconnu"),
                    "justification": res.get("justification", "")
                })
                
    except Exception as e:
        logger.error(f"Erreur Batch LLM : {e}")
        # Fallback si échec du batch : on retourne liste vide ou erreur
        stats["errors"] = 1

    logger.info(f"Anomalies détectées en {time.time() - start:.2f}s (Batch)")
    return results, stats
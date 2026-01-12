import asyncio
from dependencies import get_llm
from src.rag_setup import retrieve_context
import time
from fastapi.concurrency import run_in_threadpool

async def recommend_backup(rpo: str, rto: str, budget: str):
    start = time.time()
    # Personnalisation : stats base
    user_context = "Base utilisateur de 1GB, 50 tables, critique. Détecte changements depuis dernière backup (ex. nouvelles tables)."

    # RAG réduit
    context = "\n".join(retrieve_context("oracle backup rman rpo rto", top_k=3))

    # Lancement parallèle
    task_strategy = run_in_threadpool(
        get_llm().generate,
        f"Recommande stratégie RMAN pour RPO:{rpo}, RTO:{rto}, Budget:{budget}. Orientation DBA.",
        context=context,
        user_context=user_context
    )

    task_script = run_in_threadpool(
        get_llm().generate,
        f"Ecris uniquement un Script RMAN complet pour respecter RPO:{rpo} et RTO:{rto}.",
        context=context,
        user_context=user_context
    )

    strategy, script = await asyncio.gather(task_strategy, task_script)

    print(f"Recommandation générée en {time.time() - start:.2f}s")
    return strategy.strip(), script.strip()
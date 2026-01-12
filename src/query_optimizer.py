import asyncio
from dependencies import get_llm
from src.rag_setup import retrieve_context
from fastapi.concurrency import run_in_threadpool

async def optimize_query(sql_query: str, plan_hint: str = ""):
    context = "\n".join(retrieve_context(f"oracle query optimization {sql_query[:100]}"))
    llm = get_llm()

    # Lancement parallèle des 3 analyses
    task_explanation = run_in_threadpool(
        llm.generate,
        f"Explique en français pourquoi cette requête Oracle est lente :\n{sql_query}\nPlan : {plan_hint}",
        context=context
    )

    task_costly = run_in_threadpool(
        llm.generate,
        f"Quels sont les 3 points les plus coûteux dans cette requête ?\n{sql_query}",
        context=context
    )

    task_recommendations = run_in_threadpool(
        llm.generate,
        f"Propose 3 optimisations concrètes (index, hint, réécriture) pour cette requête :\n{sql_query}",
        context=context
    )

    explanation, costly, recommendations_text = await asyncio.gather(task_explanation, task_costly, task_recommendations)

    return {
        "explanation": explanation.strip(),
        "costly_points": costly.strip(),
        "recommendations": [line.strip() for line in recommendations_text.split('\n') if line.strip()][:3],
        "before_cost": "Élevé",
        "after_cost": "Réduit estimé"
    }
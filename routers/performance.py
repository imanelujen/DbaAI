from fastapi import APIRouter, Body
from src.query_optimizer import optimize_query
import pandas as pd

router = APIRouter(prefix="/performance", tags=["Performance"])

@router.get("/slow-queries")
async def get_slow_queries():
    try:
        df = pd.read_csv('../data/slow_queries.csv')
        queries = df.head(5).to_dict(orient='records')
        return {"queries": queries}
    except:
        return {"queries": []}

@router.post("/optimize")
async def optimize(sql: str = Body(..., embed=True)):
    result = await optimize_query(sql, "Plan probable avec Full Table Scan ou index manquant")
    return result
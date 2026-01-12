from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from src.backup_recommender import recommend_backup

router = APIRouter(prefix="/backup", tags=["Sauvegardes"])

class BackupRequest(BaseModel):
    rpo: str = "4h"       # RPO par défaut 4h
    rto: str = "2h"       # RTO par défaut 2h
    budget: str = "medium" # Budget par défaut "medium"

@router.post("/recommend")
async def recommend(request: BackupRequest):
    """
    Recommande une stratégie de sauvegarde en fonction du RPO, RTO et budget.
    Exemple de JSON body :
    {
        "rpo": "4h",
        "rto": "2h",
        "budget": "medium"
    }
    """
    try:
        strategy, script = await recommend_backup(request.rpo, request.rto, request.budget)
        return {"strategy": strategy, "script": script}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recommandation : {str(e)}")

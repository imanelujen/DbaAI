from fastapi import APIRouter
from src.anomaly_detector import detect_anomalies

router = APIRouter(prefix="/anomaly", tags=["Anomalies"])

@router.get("/")
async def get_anomalies():
    results, stats = await detect_anomalies()
    return {"results": results[:10], "stats": stats}
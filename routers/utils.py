from fastapi import APIRouter
from src.data_extractor import extract_data  # import ton fonction existante

router = APIRouter(prefix="/utils", tags=["Utilitaires"])

@router.post("/refresh-data")
async def refresh_data():
    try:
        result = extract_data()  # exécute l'extraction
        return {"status": "success", "message": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
from fastapi import APIRouter
from src.security_audit import audit_security
router = APIRouter(prefix="/security", tags=["Sécurité"])

@router.get("/")
async def get_security_report():
    report = await audit_security()
    return report
# src/api/routes/health.py
from fastapi import APIRouter

from src.core.logger_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("")
async def health_check():
    logger.debug("Verificação de saúde realizada")
    return {"status": "ok"}
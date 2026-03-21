from fastapi import APIRouter, status
from src.schemas.analytics import ClickTrack
from src.repositories.analytics_repository import analytics_repository
from datetime import datetime

router = APIRouter()

@router.post("/track-click", status_code=status.HTTP_201_CREATED)
async def track_click(payload: ClickTrack):
    payload.timestamp = datetime.now()
    
    # Salva no MongoDB para retirada fácil depois
    data = payload.model_dump()
    analytics_repository.save_click(data)
    
    email_info = f" (Email: {payload.email})" if payload.email else ""
    print(f"[ANALYTICS] Salvo no banco: {payload.elementId} (Variante: {payload.variant}){email_info}")
    
    return {"status": "tracked"}

@router.get("/stats")
async def get_stats():
    """
    Retorna as estatísticas agregadas de todos os cliques e emails capturados.
    """
    return analytics_repository.get_stats()

@router.get("/raw")
async def get_raw_data():
    """
    Retorna todos os registros brutos do banco de dados.
    """
    return {"data": analytics_repository.get_all_clicks()}

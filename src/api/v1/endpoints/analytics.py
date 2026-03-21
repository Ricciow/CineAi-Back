from fastapi import APIRouter, status, Depends
from src.schemas.analytics import ClickTrack
from src.repositories.analytics_repository import analytics_repository
from src.api.deps import get_current_user_id
from datetime import datetime

router = APIRouter()

@router.post("/track-click", status_code=status.HTTP_201_CREATED)
async def track_click(payload: ClickTrack):
    """
    Endpoint público para rastrear cliques e interesses.
    Não requer autenticação para permitir o rastreio de visitantes.
    """
    payload.timestamp = datetime.now()
    data = payload.model_dump()
    analytics_repository.save_click(data)
    
    email_info = f" (Email: {payload.email})" if payload.email else ""
    print(f"[ANALYTICS] Salvo no banco: {payload.elementId} (Variante: {payload.variant}){email_info}")
    
    return {"status": "tracked"}

@router.get("/stats")
async def get_stats(current_user_id: str = Depends(get_current_user_id)):
    """
    Retorna as estatísticas agregadas. Requer autenticação.
    """
    return analytics_repository.get_stats()

@router.get("/raw")
async def get_raw_data(current_user_id: str = Depends(get_current_user_id)):
    """
    Retorna todos os registros brutos. Requer autenticação.
    """
    return {"data": analytics_repository.get_all_clicks()}

from fastapi import APIRouter
from src.api.v1.endpoints import auth, conversation, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(conversation.router, prefix="/conversation", tags=["conversation"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

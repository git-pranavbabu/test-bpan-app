from fastapi import APIRouter
from app.api.v1.endpoints import auth, lookup, models, bpan

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(lookup.router, prefix="/lookup", tags=["Lookup Tables"])
api_router.include_router(models.router, prefix="/models", tags=["Battery Models"])
api_router.include_router(bpan.router, prefix="/bpan", tags=["BPAN"])

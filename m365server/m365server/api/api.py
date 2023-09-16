from m365server.api.endpoints import blob_storage
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(blob_storage.router, prefix="/blob_storage", tags=["blob_storage"])
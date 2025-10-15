from fastapi import APIRouter
from app.api.v1.endpoints import outlines, files, presentation

api_router = APIRouter()
api_router.include_router(outlines.router, prefix="/outlines", tags=["outlines"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(presentation.router, prefix="/presentation", tags=["presentation"])

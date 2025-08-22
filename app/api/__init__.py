from fastapi import APIRouter

from .endpoints.task import router as task_router

router = APIRouter()

router.include_router(task_router, prefix="/tasks", tags=["tasks"])


__all__ = ["router"]

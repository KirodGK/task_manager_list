from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.services.TaskService import (create_task,
                                      get_tasks,
                                      get_task,
                                      update_task,
                                      delete_task)
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.core.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Task], summary="Получить список задач")
async def read_tasks(skip: int = 0, limit: int = 100,
                     db: AsyncSession = Depends(get_db)):
    try:
        tasks = await get_tasks(db, skip=skip, limit=limit)
        return tasks
    except Exception as e:
        logger.error(f"Database error in read_tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED,
             summary="Создать новую задачу")
async def create_new_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_task(db=db, task=task)
    except Exception as e:
        logger.error(f"Database error in create_task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{task_uuid}", response_model=Task,
            summary="Получить задачу по UUID")
async def read_task(task_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        db_task = await get_task(db, task_uuid=task_uuid)
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return db_task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in read_task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{task_uuid}", response_model=Task, summary="Обновить задачу")
async def update_existing_task(task_uuid: str, task_update: TaskUpdate,
                               db: AsyncSession = Depends(get_db)):
    try:
        db_task = await update_task(db, task_uuid=task_uuid,
                                    task_update=task_update)
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return db_task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in update_task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{task_uuid}", summary="Удалить задачу")
async def delete_existing_task(task_uuid: str,
                               db: AsyncSession = Depends(get_db)):
    try:
        db_task = await delete_task(db, task_uuid=task_uuid)
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in delete_task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

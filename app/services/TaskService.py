from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, task: TaskCreate) -> Task:
    db_task = Task(**task.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def get_task(db: AsyncSession, task_uuid: str) -> Task | None:
    stmt = select(Task).where(Task.uuid == task_uuid)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Task]:
    stmt = select(Task).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_task(db: AsyncSession, task_uuid: str, task_update: TaskUpdate) -> Task | None:
    db_task = await get_task(db, task_uuid)
    if db_task:
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(db_task, field, value)
        await db.commit()
        await db.refresh(db_task)
        return db_task


async def delete_task(db: AsyncSession, task_uuid: str) -> Task | None:
    db_task = await get_task(db, task_uuid)
    if db_task:
        await db.delete(db_task)
        await db.commit()
        return db_task

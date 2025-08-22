# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
import os
from app.main import app
from app.core.db import get_db

# Используем асинхронный PostgreSQL для основного приложения в тестах
# Если запускаете тесты через docker-compose exec web pytest tests/, используйте 'db'
# Если запускаете локально (pytest tests/), используйте 'localhost'
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    # Используем 'db' для Docker
    "postgresql+asyncpg://postgres:postgres@db:5432/task_manager"
    # "postgresql+asyncpg://postgres:postgres@localhost:5432/task_manager" # Раскомментируйте для локального запуска
)

# Создаем асинхронный движок для тестов (для приложения)
async_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Создаем СИНХРОННЫЙ движок ТОЛЬКО для очистки базы
# Это часто более надежно для операций TRUNCATE в фикстурах
sync_engine = create_engine(TEST_DATABASE_URL.replace(
    "postgresql+asyncpg://", "postgresql+psycopg2://"))

# Функция для переопределения зависимости get_db


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

# Переопределяем зависимость в приложении
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def client():
    """Фикстура для тестового клиента"""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function", autouse=True)
def cleanup_database():
    """Очистка базы данных перед и после каждым тестом"""
    # СИНХРОННАЯ Очистка перед тестом
    try:
        with sync_engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text("TRUNCATE TABLE tasks RESTART IDENTITY CASCADE"))
        # print("DEBUG: База очищена ПЕРЕД тестом")
    except Exception as e:
        print(f"Предупреждение: Не удалось очистить базу перед тестом: {e}")

    yield  # Здесь выполняется тест

    # СИНХРОННАЯ Очистка после теста
    try:
        with sync_engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text("TRUNCATE TABLE tasks RESTART IDENTITY CASCADE"))
        # print("DEBUG: База очищена ПОСЛЕ теста")
    except Exception as e:
        print(f"Предупреждение: Не удалось очистить базу после теста: {e}")


@pytest.fixture
def task_data():
    """Фикстура с базовыми данными для задачи"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "created"
    }


@pytest.fixture
def task_update_data():
    """Фикстура с данными для обновления задачи"""
    return {
        "title": "Updated Task",
        "description": "This task has been updated",
        "status": "in_progress"
    }

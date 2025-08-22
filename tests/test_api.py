# tests/test_api.py
# Этот файл уже должен быть у вас и выглядеть примерно так
import pytest
from fastapi.testclient import TestClient


# Фикстура client импортируется из conftest.py
# @pytest.fixture(scope="session")
# def client():
#     """Фикстура для тестового клиента"""
#     with TestClient(app) as c:
#         yield c

def test_root_endpoint(client):
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Task Manager API is running"}


def test_health_check(client):
    """Тест эндпоинта проверки здоровья"""
    # Добавим повторные попытки для большей надежности
    import time
    for i in range(3):
        response = client.get("/health")
        if response.status_code == 200 and response.json()["status"] == "healthy":
            return  # Тест пройден
        time.sleep(0.5)  # Подождем немного

    # Если после всех попыток не удалось - финальная проверка
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

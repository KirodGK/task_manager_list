# tests/test_tasks.py
# Этот файл уже должен быть у вас и выглядеть примерно так
from uuid import UUID

# Все фикстуры (client, task_data, task_update_data, cleanup_database) импортируются из conftest.py


class TestTaskCRUD:
    """Тесты для CRUD операций с задачами"""

    def test_create_task(self, client, task_data):
        """Тест создания задачи"""
        response = client.post("/tasks/", json=task_data)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]
        # Проверяем, что UUID валидный
        assert UUID(data["uuid"])

    def test_create_task_without_description(self, client):
        """Тест создания задачи без описания"""
        task_data = {
            "title": "Task without description",
            "status": "created"
        }
        response = client.post("/tasks/", json=task_data)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] is None
        assert data["status"] == task_data["status"]

    def test_get_tasks_empty(self, client):
        """Тест получения списка задач (пустой список)"""
        # Убедимся, что база пустая
        response = client.get("/tasks/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_tasks_with_pagination(self, client, task_data):
        """Тест получения списка задач с пагинацией"""
        # Создаем несколько задач
        for i in range(5):
            task_data["title"] = f"Task {i}"
            client.post("/tasks/", json=task_data)

        # Получаем первую страницу (по умолчанию limit=100)
        response = client.get("/tasks/")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 5

        # Получаем с ограничением
        response = client.get("/tasks/?limit=2")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2

        # Получаем со смещением
        response = client.get("/tasks/?skip=2&limit=2")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2

    def test_get_task_by_uuid(self, client, task_data):
        """Тест получения задачи по UUID"""
        # Сначала создаем задачу
        create_response = client.post("/tasks/", json=task_data)
        task_uuid = create_response.json()["uuid"]

        # Получаем задачу по UUID
        response = client.get(f"/tasks/{task_uuid}")
        assert response.status_code == 200

        data = response.json()
        assert data["uuid"] == task_uuid
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]

    def test_get_task_not_found(self, client):
        """Тест получения несуществующей задачи"""
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/tasks/{fake_uuid}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_update_task(self, client, task_data, task_update_data):
        """Тест обновления задачи"""
        # Создаем задачу
        create_response = client.post("/tasks/", json=task_data)
        task_uuid = create_response.json()["uuid"]

        # Обновляем задачу
        response = client.put(f"/tasks/{task_uuid}", json=task_update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["uuid"] == task_uuid
        assert data["title"] == task_update_data["title"]
        assert data["description"] == task_update_data["description"]
        assert data["status"] == task_update_data["status"]

    def test_update_task_partial(self, client, task_data):
        """Тест частичного обновления задачи"""
        # Создаем задачу
        create_response = client.post("/tasks/", json=task_data)
        task_uuid = create_response.json()["uuid"]

        # Обновляем только заголовок
        update_data = {"title": "Partially Updated Title"}
        response = client.put(f"/tasks/{task_uuid}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Partially Updated Title"
        # Остальные поля должны остаться прежними
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]

    def test_update_task_not_found(self, client, task_update_data):
        """Тест обновления несуществующей задачи"""
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.put(f"/tasks/{fake_uuid}", json=task_update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_delete_task(self, client, task_data):
        """Тест удаления задачи"""
        # Создаем задачу
        create_response = client.post("/tasks/", json=task_data)
        task_uuid = create_response.json()["uuid"]

        # Удаляем задачу
        response = client.delete(f"/tasks/{task_uuid}")
        assert response.status_code == 200
        assert response.json()["message"] == "Task deleted successfully"

        # Проверяем, что задача больше не существует
        get_response = client.get(f"/tasks/{task_uuid}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client):
        """Тест удаления несуществующей задачи"""
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.delete(f"/tasks/{fake_uuid}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_create_task_invalid_data(self, client):
        """Тест создания задачи с невалидными данными"""
        # Пустые данные
        response = client.post("/tasks/", json={})
        assert response.status_code == 422

        # Данные без обязательного поля title
        invalid_data = {"description": "No title"}
        response = client.post("/tasks/", json=invalid_data)
        assert response.status_code == 422

    def test_update_task_invalid_status(self, client, task_data):
        """Тест обновления задачи с невалидным статусом"""
        # Создаем задачу
        create_response = client.post("/tasks/", json=task_data)
        task_uuid = create_response.json()["uuid"]

        # Пытаемся обновить с невалидным статусом
        invalid_update = {"status": "invalid_status"}
        response = client.put(f"/tasks/{task_uuid}", json=invalid_update)
        assert response.status_code == 422

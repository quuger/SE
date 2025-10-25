"""
Интеграционные тесты для закладок
"""
import sys
import os
import pytest
from httpx import AsyncClient
from uuid import uuid4

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBookmarks:
    """Тесты для эндпоинтов закладок"""
    
    async def test_get_bookmarks_unauthorized(self, client: AsyncClient):
        """Тест получения закладок без авторизации"""
        response = await client.get("/bookmarks/")
        
        assert response.status_code in [401, 403], response.text
    
    async def test_get_bookmarks_empty(self, client: AsyncClient, auth_headers):
        """Тест получения пустого списка закладок"""
        response = await client.get("/bookmarks/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "bookmarks" in data
        assert "total_count" in data
        assert "has_more" in data
        assert data["bookmarks"] == []
        assert data["total_count"] == 0
        assert data["has_more"] is False
    
    async def test_get_bookmarks_with_data(self, client: AsyncClient, auth_headers, multiple_bookmarks):
        """Тест получения закладок с данными"""
        response = await client.get("/bookmarks/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["bookmarks"]) == 5
        assert data["total_count"] == 5
        assert data["has_more"] is False
        
        # Проверяем структуру закладки
        bookmark = data["bookmarks"][0]
        assert "id" in bookmark
        assert "url" in bookmark
        assert "title" in bookmark
        assert "description" in bookmark
        assert "status" in bookmark
        assert "access_level" in bookmark
        assert "owner_id" in bookmark
        assert "sync_version" in bookmark
        assert "created_at" in bookmark
    
    async def test_get_bookmarks_pagination(self, client: AsyncClient, auth_headers, multiple_bookmarks):
        """Тест пагинации закладок"""
        # Первая страница
        response = await client.get("/bookmarks/?limit=2&offset=0", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["bookmarks"]) == 2
        assert data["total_count"] == 5
        assert data["has_more"] is True
        
        # Вторая страница
        response = await client.get("/bookmarks/?limit=2&offset=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["bookmarks"]) == 2
        assert data["total_count"] == 5
        assert data["has_more"] is True
        
        # Последняя страница
        response = await client.get("/bookmarks/?limit=2&offset=4", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["bookmarks"]) == 1
        assert data["total_count"] == 5
        assert data["has_more"] is False
    
    async def test_get_bookmarks_invalid_pagination(self, client: AsyncClient, auth_headers):
        """Тест невалидной пагинации"""
        # Отрицательный limit
        response = await client.get("/bookmarks/?limit=-1", headers=auth_headers)
        assert response.status_code == 422
        
        # Слишком большой limit
        response = await client.get("/bookmarks/?limit=1000", headers=auth_headers)
        assert response.status_code == 422
        
        # Отрицательный offset
        response = await client.get("/bookmarks/?offset=-1", headers=auth_headers)
        assert response.status_code == 422
    
    async def test_create_bookmark_success(self, client: AsyncClient, auth_headers):
        """Тест успешного создания закладки"""
        bookmark_data = {
            "url": "https://example.com",
            "title": "Test Bookmark",
            "description": "Test description",
            "access_level": "private"
        }
        
        response = await client.post("/bookmarks/", json=bookmark_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["url"] == bookmark_data["url"] or data["url"] == bookmark_data["url"] + "/" or data["url"] == bookmark_data["url"] + "/"
        assert data["title"] == bookmark_data["title"]
        assert data["description"] == bookmark_data["description"]
        assert data["access_level"] == bookmark_data["access_level"]
        assert data["status"] == "active"
        assert "id" in data
        assert "owner_id" in data
        assert "sync_version" in data
        assert "created_at" in data
    
    async def test_create_bookmark_minimal_data(self, client: AsyncClient, auth_headers):
        """Тест создания закладки с минимальными данными"""
        bookmark_data = {
            "url": "https://minimal.com",
            "title": "Minimal Bookmark"
        }
        
        response = await client.post("/bookmarks/", json=bookmark_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["url"] == bookmark_data["url"] or data["url"] == bookmark_data["url"] + "/"
        assert data["title"] == bookmark_data["title"]
        assert data["description"] is None
        assert data["access_level"] == "private"  # Default value
    
    async def test_create_bookmark_unauthorized(self, client: AsyncClient):
        """Тест создания закладки без авторизации"""
        bookmark_data = {
            "url": "https://example.com",
            "title": "Test Bookmark"
        }
        
        response = await client.post("/bookmarks/", json=bookmark_data)
        
        assert response.status_code in [401, 403]  # Ошибка авторизации
    
    async def test_create_bookmark_invalid_url(self, client: AsyncClient, auth_headers):
        """Тест создания закладки с невалидным URL"""
        bookmark_data = {
            "url": "not-a-url",
            "title": "Test Bookmark"
        }
        
        response = await client.post("/bookmarks/", json=bookmark_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    async def test_create_bookmark_long_title(self, client: AsyncClient, auth_headers):
        """Тест создания закладки с слишком длинным заголовком"""
        bookmark_data = {
            "url": "https://example.com",
            "title": "x" * 300  # Превышает лимит в 255 символов
        }
        
        response = await client.post("/bookmarks/", json=bookmark_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    async def test_create_bookmark_long_description(self, client: AsyncClient, auth_headers):
        """Тест создания закладки с слишком длинным описанием"""
        bookmark_data = {
            "url": "https://example.com",
            "title": "Test Bookmark",
            "description": "x" * 1100  # Превышает лимит в 1000 символов
        }
        
        response = await client.post("/bookmarks/", json=bookmark_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    async def test_create_bookmark_missing_fields(self, client: AsyncClient, auth_headers):
        """Тест создания закладки с отсутствующими полями"""
        # Без URL
        response = await client.post("/bookmarks/", json={"title": "Test"}, headers=auth_headers)
        assert response.status_code == 422
        
        # Без title
        response = await client.post("/bookmarks/", json={"url": "https://example.com"}, headers=auth_headers)
        assert response.status_code == 422
    
    async def test_update_bookmark_success(self, client: AsyncClient, auth_headers, test_bookmark):
        """Тест успешного обновления закладки"""
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "access_level": "public"
        }
        
        response = await client.put(
            f"/bookmarks/{test_bookmark.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["access_level"] == update_data["access_level"]
        assert data["url"] == test_bookmark.url or data["url"] == test_bookmark.url + "/"  # Не изменилось
        assert data["sync_version"] >= test_bookmark.sync_version  # Версия увеличилась или осталась той же
    
    async def test_update_bookmark_partial(self, client: AsyncClient, auth_headers, test_bookmark):
        """Тест частичного обновления закладки"""
        update_data = {
            "title": "Only Title Updated"
        }
        
        response = await client.put(
            f"/bookmarks/{test_bookmark.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == update_data["title"]
        assert data["description"] == test_bookmark.description  # Не изменилось
        assert data["url"] == test_bookmark.url or data["url"] == test_bookmark.url + "/"  # Не изменилось
    
    async def test_update_bookmark_not_found(self, client: AsyncClient, auth_headers):
        """Тест обновления несуществующей закладки"""
        update_data = {"title": "Updated Title"}
        
        response = await client.put(
            f"/bookmarks/{uuid4()}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    async def test_update_bookmark_unauthorized(self, client: AsyncClient, test_bookmark):
        """Тест обновления закладки без авторизации"""
        update_data = {"title": "Updated Title"}
        
        response = await client.put(f"/bookmarks/{test_bookmark.id}", json=update_data)
        
        assert response.status_code in [401, 403]  # Ошибка авторизации
    
    async def test_update_bookmark_wrong_owner(self, client: AsyncClient, auth_headers, test_user_2):
        """Тест обновления закладки другого пользователя"""
        # Создаем закладку для другого пользователя
        bookmark_data = {
            "url": "https://other.com",
            "title": "Other User Bookmark"
        }
        
        # Создаем токен для второго пользователя
        login_data = {
            "email": test_user_2.email,
            "password": "pass123"
        }
        
        response = await client.post("/auth/login", json=login_data)
        other_auth_headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
        
        response = await client.post("/bookmarks/", json=bookmark_data, headers=other_auth_headers)
        other_bookmark_id = response.json()["id"]
        
        # Пытаемся обновить закладку другого пользователя
        update_data = {"title": "Hacked Title"}
        
        response = await client.put(
            f"/bookmarks/{other_bookmark_id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 404  # Не найдена для текущего пользователя
    
    async def test_delete_bookmark_success(self, client: AsyncClient, auth_headers, test_bookmark):
        """Тест успешного удаления закладки"""
        response = await client.delete(f"/bookmarks/{test_bookmark.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Проверяем, что закладка действительно удалена
        response = await client.get("/bookmarks/", headers=auth_headers)
        bookmarks = response.json()["bookmarks"]
        bookmark_ids = [b["id"] for b in bookmarks]
        assert str(test_bookmark.id) not in bookmark_ids
    
    async def test_delete_bookmark_not_found(self, client: AsyncClient, auth_headers):
        """Тест удаления несуществующей закладки"""
        response = await client.delete(f"/bookmarks/{uuid4()}", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    async def test_delete_bookmark_unauthorized(self, client: AsyncClient, test_bookmark):
        """Тест удаления закладки без авторизации"""
        response = await client.delete(f"/bookmarks/{test_bookmark.id}")
        
        assert response.status_code in [401, 403]  # Ошибка авторизации
    
    async def test_delete_bookmark_wrong_owner(self, client: AsyncClient, auth_headers, test_user_2):
        """Тест удаления закладки другого пользователя"""
        # Создаем закладку для другого пользователя
        bookmark_data = {
            "url": "https://other.com",
            "title": "Other User Bookmark"
        }
        
        # Создаем токен для второго пользователя
        login_data = {
            "email": test_user_2.email,
            "password": "pass123"
        }
        
        response = await client.post("/auth/login", json=login_data)
        other_auth_headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
        
        response = await client.post("/bookmarks/", json=bookmark_data, headers=other_auth_headers)
        other_bookmark_id = response.json()["id"]
        
        # Пытаемся удалить закладку другого пользователя
        response = await client.delete(f"/bookmarks/{other_bookmark_id}", headers=auth_headers)
        
        assert response.status_code == 404  # Не найдена для текущего пользователя

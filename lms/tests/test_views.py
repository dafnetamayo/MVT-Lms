import pytest
from rest_framework.test import APIClient
from lms.tests.factories import CategoryFactory
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestCategoryAPI:
    endpoint = "/api/lms/categories/"

    def setup_method(self):
        self.client = APIClient()

    def _auth_client(self):
        user = User.objects.create_user(
            username="tester", password="password123")
        self.client.force_authenticate(user=user)
        return user

    def test_list_categories(self):
        """Debe listar las categorías existentes"""
        CategoryFactory.create_batch(3)
        response = self.client.get(self.endpoint)
        assert response.status_code == 200
        assert response.json()["count"] == 3

    def test_create_category(self):
        """Debe crear una categoría nueva"""
        # authenticate before creating
        self._auth_client()
        payload = {"name": "Science", "description": "STEM courses"}
        response = self.client.post(self.endpoint, payload, format="json")

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Science"
        assert data["color"] == "#007bff"

    def test_retrieve_category(self):
        """Debe recuperar una categoría específica"""
        category = CategoryFactory(name="Art")
        response = self.client.get(f"{self.endpoint}{category.id}/")

        assert response.status_code == 200
        assert response.json()["name"] == "Art"

    def test_update_category(self):
        """Debe actualizar una categoría existente"""
        category = CategoryFactory(name="Old Name")
        # authenticate before updating
        self._auth_client()
        payload = {"name": "Updated Name"}
        response = self.client.patch(
            f"{self.endpoint}{category.id}/", payload, format="json")

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_delete_category(self):
        """Debe eliminar una categoría"""
        category = CategoryFactory()
        # authenticate before deleting
        self._auth_client()
        response = self.client.delete(f"{self.endpoint}{category.id}/")
        assert response.status_code == 204

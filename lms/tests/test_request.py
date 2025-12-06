import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_full_category_crud_flow():
    client = APIClient()
    endpoint = "/api/lms/categories/"
    # Autenticar cliente
    user = User.objects.create_user(
        username="tester", password="password123")
    client.force_authenticate(user=user)

    create_res = client.post(endpoint, {"name": "Physics"}, format="json")
    assert create_res.status_code == 201
    cat_id = create_res.json()["id"]

    # Leer
    list_res = client.get(endpoint)
    assert len(list_res.json()) == 4  # Asumiendo que no hay categorías previas

    # Actualizar
    update_res = client.patch(
        f"{endpoint}{cat_id}/", {"color": "#ff0000"}, format="json")
    assert update_res.status_code == 200
    assert update_res.json()["color"] == "#ff0000"

    # Eliminar
    delete_res = client.delete(f"{endpoint}{cat_id}/")
    assert delete_res.status_code == 204

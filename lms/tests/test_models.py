import pytest
from lms.models import Category
from django.db import IntegrityError


@pytest.mark.django_db
class TestCategoryModel:
    def test_create_category_successfully(self):
        """Debe crear una categoría con valores válidos"""
        category = Category.objects.create(
            name="Programming",
            description="Courses related to software development",
            color="#00ff00"
        )

        assert category.id is not None
        assert category.name == "Programming"
        assert category.color == "#00ff00"
        assert category.description.startswith("Courses")
        assert str(category) == "Programming"

    def test_name_must_be_unique(self):
        """Debe lanzar error si se intenta crear una categoría duplicada"""
        Category.objects.create(name="Design")
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Design")

    def test_default_color_and_created_at(self):
        """Debe asignar color por defecto y fecha de creación automáticamente"""
        category = Category.objects.create(name="Art")
        assert category.color == "#007bff"
        assert category.created_at is not None

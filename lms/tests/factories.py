import factory
from lms.models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    color = factory.Faker("hex_color")

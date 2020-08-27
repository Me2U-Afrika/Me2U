import factory
import factory.fuzzy
from asgiref.sync import sync_to_async
from me2ushop import models

from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    email = 'user@site.com'
    username = 'dmax28'

    class Meta:
        model = User
        django_get_or_create = ('email', 'username',)


class ProductFactory(factory.django.DjangoModelFactory):
    price = factory.fuzzy.FuzzyDecimal(1.0, 1000.0, 2)

    class Meta:
        model = models.Product


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Address


class OrderItemFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.OrderItem


class OrderFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Order

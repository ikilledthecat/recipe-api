from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGRIDIENTS_URL = reverse('recipe:ingredient-list')

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        email='email@test.com',
        password='bar8947',
        name='test name'
    )


def test_ingredients_login_required(client):
    """Test a login is required to dta from tags api"""
    res = client.get(INGRIDIENTS_URL)

    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_ingredients_list_view(client, user):
    """Test tags api returns all tags in database"""
    Ingredient.objects.create(user=user, name='Tomato')
    Ingredient.objects.create(user=user, name='Potato')

    client.force_authenticate(user=user)
    res = client.get(INGRIDIENTS_URL)

    tags = Ingredient.objects.all().order_by('-name')
    serializer = IngredientSerializer(tags, many=True)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == serializer.data


def test_ingredients_list_view_limited_user(client, user):
    """Test tags api returns all tags in database"""
    alt_user = get_user_model().objects.create_user(
        email='email_alt@test.com',
        password='bar8947',
        name='test name alt'
    )
    Ingredient.objects.create(user=user, name='Cucumber')
    Ingredient.objects.create(user=user, name='Tomato')
    Ingredient.objects.create(user=alt_user, name='Potato')
    Ingredient.objects.create(user=alt_user, name='Gourd')

    client.force_authenticate(user=user)
    res = client.get(INGRIDIENTS_URL)

    tags = Ingredient.objects.filter(user=user).all().order_by('-name')
    serializer = IngredientSerializer(tags, many=True)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == serializer.data


def test_create_ingredient_successful(client, user):
    """Test ingredients api creates new tags in the database"""
    payload = {'name': 'Beans'}
    client.force_authenticate(user=user)
    client.post(INGRIDIENTS_URL, payload)
    exists = Ingredient\
        .objects\
        .filter(name=payload['name'], user=user)\
        .exists()
    assert exists


def test_create_ingredient_unsuccessful(client, user):
    """Test ingredients api fails to create new ingredient with invalid name"""
    payload = {'name': ''}
    client.force_authenticate(user=user)
    client.post(Ingredient, payload)
    exists = Ingredient\
        .objects\
        .filter(name=payload['name'], user=user)\
        .exists()
    assert not exists

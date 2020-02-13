from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient, Tag

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')

pytestmark = pytest.mark.django_db


def sample_recipe(user, **params):
    """Create and Return a sample recipe"""
    defaults = {
        'name': 'Sample Recipe',
        'time_minutes': 10,
        'price': 4.00,
        'user': user
    }
    defaults.update(params)
    return Recipe.objects.create(**defaults)


def sample_ingredient(user, name='Cinnamon'):
    """Create and Return a sample recipe"""
    return Ingredient.objects.create(user=user, name=name)


def sample_tag(user, name='Asian'):
    """Create and Return a sample recipe"""
    return Tag.objects.create(user=user, name=name)


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


def test_recipes_login_required(client):
    """Test a login is required to query tags api"""
    res = client.get(RECIPES_URL)

    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_recipes_list_view(client, user):
    """Test recipes api returns all recipes in database"""
    sample_recipe(user=user, name='Sample Recipe 1')
    sample_recipe(user=user, name='Sample Recipe 2')

    client.force_authenticate(user=user)
    res = client.get(RECIPES_URL)

    recipes = Recipe.objects.all().order_by('-name')
    serializer = RecipeSerializer(recipes, many=True)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == serializer.data


def test_recipes_list_view_limited_user(client, user):
    """Test recipes api returns all tags in database"""
    alt_user = get_user_model().objects.create_user(
        email='email_alt@test.com',
        password='bar8947',
        name='test name alt'
    )
    sample_recipe(user=user, name='Sample Recipe 1')
    sample_recipe(user=user, name='Sample Recipe 2')
    sample_recipe(user=alt_user, name='Sample Recipe 3')
    sample_recipe(user=alt_user, name='Sample Recipe 4')

    client.force_authenticate(user=user)
    res = client.get(RECIPES_URL)

    recipes = Recipe.objects.filter(user=user).all().order_by('-name')
    serializer = RecipeSerializer(recipes, many=True)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == serializer.data


def test_create_recipe_successful(client, user):
    """Test recipes api creates new recipes in the database"""
    payload = {'name': 'Pho', 'price': 15.00, 'time_minutes': 30}
    client.force_authenticate(user=user)
    res = client.post(RECIPES_URL, payload)
    recipe = Recipe.objects.get(id=res.data['id'])
    assert res.status_code == status.HTTP_201_CREATED
    assert all(getattr(recipe, k) == v for k, v in payload.items())


def test_create_recipe_with_tag_successful(client, user):
    """Test recipes api creates new recipes with tags in the database"""
    tag1 = sample_tag(user, name='Dessert')
    tag2 = sample_tag(user, name='Asian')
    payload = {
        'name': 'Pho', 'price': 15.00, 'time_minutes': 30,
        'tags': [tag1.id, tag2.id]
    }
    client.force_authenticate(user=user)
    res = client.post(RECIPES_URL, payload)
    recipe = Recipe.objects.get(id=res.data['id'])
    assert res.status_code == status.HTTP_201_CREATED
    assert all(
        getattr(recipe, k) == v for k, v in payload.items() if k != 'tags'
    )
    assert recipe.tags.all().count() == 2
    assert tag1 in recipe.tags.all()
    assert tag2 in recipe.tags.all()


def test_create_recipe_with_ingredient_successful(client, user):
    """Test recipes api creates new recipes with tags in the database"""
    ingredient1 = sample_ingredient(user, name='Sugar')
    ingredient2 = sample_ingredient(user, name='Flour')
    payload = {
        'name': 'Pho', 'price': 15.00, 'time_minutes': 30,
        'ingredients': [ingredient1.id, ingredient2.id]
    }
    client.force_authenticate(user=user)
    res = client.post(RECIPES_URL, payload)
    recipe = Recipe.objects.get(id=res.data['id'])
    assert res.status_code == status.HTTP_201_CREATED
    assert all(
        getattr(recipe, k) == v for k, v in payload.items()
        if k != 'ingredients'
    )
    assert recipe.ingredients.all().count() == 2
    assert ingredient1 in recipe.ingredients.all()
    assert ingredient2 in recipe.ingredients.all()


def test_create_recipe_unsuccessful(client, user):
    """Test recipes api fails to create new recipe with invalid name"""
    payload = {'name': '', 'price': 15.00, 'time_minutes': 30}
    client.force_authenticate(user=user)
    client.post(RECIPES_URL, payload)
    exists = Recipe.objects.filter(
        name=payload['name'], user=user, price=payload['price'],
        time_minutes=payload['time_minutes']
        )\
        .exists()
    assert not exists


def test_get_recipe_successful(client, user):
    """Test recipes api fails to create new recipe with invalid name"""
    payload = {'name': 'Pho', 'price': 15.00, 'time_minutes': 30}
    recipe = sample_recipe(user, **payload)
    recipe.tags.add(sample_tag(user))
    recipe.ingredients.add(sample_ingredient(user))
    recipe.save()
    uri = reverse('recipe:recipe-detail', args=[recipe.id])
    client.force_authenticate(user=user)
    res = client.get(uri)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == RecipeDetailSerializer(recipe, many=False).data


def test_update_recipe_successful(client, user):
    """Test recipes api fails to create new recipe with invalid name"""
    payload = {'name': 'Pho', 'price': 15.00, 'time_minutes': 30}
    recipe = sample_recipe(user, **payload)
    uri = reverse('recipe:recipe-detail', args=[recipe.id])
    client.force_authenticate(user=user)
    client.patch(uri, {'name': 'Steak'})
    recipe.refresh_from_db()
    assert recipe.name == 'Steak'

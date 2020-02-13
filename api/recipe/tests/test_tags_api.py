from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')

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


def test_tags_login_required(client):
    """Test a login is required to dta from tags api"""
    res = client.get(TAGS_URL)

    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_tags_list_view(client, user):
    """Test tags api returns all tags in database"""
    Tag.objects.create(user=user, name='Vegan')
    Tag.objects.create(user=user, name='Mexican')

    client.force_authenticate(user=user)
    res = client.get(TAGS_URL)

    tags = Tag.objects.all().order_by('-name')
    serializer = TagSerializer(tags, many=True)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == serializer.data


def test_tags_list_view_limited_user(client, user):
    """Test tags api returns all tags in database"""
    alt_user = get_user_model().objects.create_user(
        email='email_alt@test.com',
        password='bar8947',
        name='test name alt'
    )
    Tag.objects.create(user=user, name='Vegan')
    Tag.objects.create(user=user, name='Mexican')
    Tag.objects.create(user=alt_user, name='Indian')
    Tag.objects.create(user=alt_user, name='Japanese')

    client.force_authenticate(user=user)
    res = client.get(TAGS_URL)

    tags = Tag.objects.filter(user=user).all().order_by('-name')
    serializer = TagSerializer(tags, many=True)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == serializer.data


def test_create_tag_successful(client, user):
    """Test tags api creates new tags in the database"""
    payload = {'name': 'Vietnamese'}
    client.force_authenticate(user=user)
    client.post(TAGS_URL, payload)
    exists = Tag.objects.filter(name=payload['name'], user=user).exists()
    assert exists


def test_create_tag_unsuccessful(client, user):
    """Test tags api fails to create new tag with invalid name"""
    payload = {'name': ''}
    client.force_authenticate(user=user)
    client.post(TAGS_URL, payload)
    exists = Tag.objects.filter(name=payload['name'], user=user).exists()
    assert not exists

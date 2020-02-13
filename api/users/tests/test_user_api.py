import pytest


from django.contrib.auth import get_user_model
from django.urls import reverse


from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')
ME_URL = reverse('users:me')


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def users():
    usrs = []
    for i in range(5):
        usrs.append(
            create_user('email-%d@test.com' % i, 'password %d' % i)
        )
    return usrs


@pytest.fixture
def super_users():
    usrs = []
    for i in range(5):
        usrs.append(
            create_user('email-%d@test.com' % i, 'password %d' % i)
        )
    return usrs


def create_user(email, password, **kwargs):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        **kwargs
    )


@pytest.mark.django_db
def test_create_valid_user(client):
    """Test creating a user using a vlaid payload"""
    payload = {
        'email': 'test@gmail.com',
        'password': 'testpassword',
        'name': 'Test Hero',
    }
    res = client.post(CREATE_USER_URL, payload)

    assert res.status_code == status.HTTP_201_CREATED
    user = get_user_model().objects.get(email=payload['email'])
    assert user.check_password(payload['password'])
    assert 'password' not in res.data


@pytest.mark.django_db
def test_user_exists(client, users):
    """Test creating a user who already exists fails"""
    payload = {
        'email': users[0].email,
        'password': users[0].password,
        'name': users[0].name,
    }
    res = client.post(CREATE_USER_URL, payload)

    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_with_short_password(client, users):
    """Test creating a user with short password fails"""
    payload = {
        'email': 'shortp@gmail.com',
        'password': 'p',
        'name': 'short password',
    }
    res = client.post(CREATE_USER_URL, payload)

    assert res.status_code == status.HTTP_400_BAD_REQUEST
    user_exists = get_user_model()\
        .objects\
        .filter(email=payload['email'])\
        .exists()
    assert not user_exists


@pytest.mark.django_db
def test_create_token_for_user(client, users):
    """Test token generation for user"""
    payload = {
        'email': 'test@example.com',
        'password': 'test12345',
        'name': 'Test User'
    }
    create_user(**payload)
    payload = {'email': payload['email'], 'password': payload['password']}
    res = client.post(TOKEN_URL, payload)

    assert 'token' in res.data
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_token_invalid_credentials(client, users):
    user = users[0]
    payload = {
        'email': user.email,
        'password': 'p',
    }
    res = client.post(TOKEN_URL, payload)
    assert 'token' not in res.data
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_token_no_user(client):
    payload = {
        'email': 'shortp@gmail.com',
        'password': 'p',
    }
    res = client.post(TOKEN_URL, payload)
    assert 'token' not in res.data
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_token_missing_data(client):
    payload = {
        'email': 'shortp@gmail.com',
        'password': '',
    }
    res = client.post(TOKEN_URL, payload)
    assert 'token' not in res.data
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_retrieve_user_unauthorized(client):
    """Authentication is required to retriever user url"""
    resp = client.get(ME_URL)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_user_authorized(client, django_user_model):
    """Authenticated user should be able to acess info"""
    email = "email@test.com"
    password = "bar8947"
    name = 'test name'
    user = django_user_model.objects.create_user(
        email=email, password=password, name=name
    )
    client.force_authenticate(user=user)
    resp = client.get(ME_URL)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {'email': email, 'name': name}


@pytest.mark.django_db
def test_post_me_not_allowed(client, django_user_model):
    email = "email@test.com"
    password = "bar8947"
    name = 'test name'
    user = django_user_model.objects.create_user(
        email=email, password=password, name=name
    )
    client.force_authenticate(user=user)
    res = client.post(ME_URL, email=email, password=password, name=name)
    assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_update_me_user_authorized(client, django_user_model):
    email = "email@test.com"
    password = "bar8947"
    name = 'test name'
    user = django_user_model.objects.create_user(
        email=email, password=password, name=name
    )
    client.force_authenticate(user=user)
    res = client.patch(
        ME_URL,
        {'name': 'New Name', 'password': 'new password'}
    )
    user.refresh_from_db()
    assert user.name == 'New Name'
    assert user.check_password('new password')
    assert res.status_code == status.HTTP_200_OK

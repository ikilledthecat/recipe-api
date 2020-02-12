import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.fixture
def admin_user(client):
    admin_user = get_user_model().objects.create_superuser(
        email='admin@example.com',
        password='password',
    )
    client.force_login(admin_user)
    return admin_user


@pytest.fixture
def user():
    return get_user_model().objects.create_superuser(
        email='user@example.com',
        password='password',
    )


@pytest.mark.django_db
def test_users_listed(client, admin_user, user):
    """ Test that users are listed on the user admin page"""
    url = reverse('admin:core_user_changelist')
    res = client.get(url)

    assert user.name in res.rendered_content
    assert user.email in res.rendered_content


@pytest.mark.django_db
def test_user_change(client, admin_user, user):
    """ Test that user change page is rendered through admin"""
    url = reverse('admin:core_user_change', args=[user.id])
    res = client.get(url)

    assert res.status_code == 200


@pytest.mark.django_db
def test_user_create(client, admin_user, user):
    """ Test that user create page is rendered through admin"""
    url = reverse('admin:core_user_add')
    res = client.get(url)

    assert res.status_code == 200

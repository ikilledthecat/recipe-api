import pytest
from django.contrib.auth import get_user_model
from core import models


pytestmark = pytest.mark.django_db


def sample_user(email='test@gmail.com', password='password', name='test user'):
    return get_user_model().objects.create_user(
        email=email, password=password, name=name
    )


def test_create_user_with_email_success():
    "test creating a new user with email is successful"
    test_email = "example@example.com"
    password = "password123"
    user = get_user_model().objects.create_user(
        email=test_email,
        password=password
    )
    assert user.email == test_email
    assert user.check_password(password)


def test_create_user_with_email_normalize_success():
    "test creating a new user with email is normalized"
    test_email = "example@EXAMPLe.com"
    password = "password123"
    user = get_user_model().objects.create_user(
        email=test_email,
        password=password
    )
    assert user.email == test_email.lower()


def test_create_user_with_invalid_email_failure():
    "test creating a new user with invalid email is unsuccessful"
    with pytest.raises(AttributeError) as excinfo:
        test_email = None
        password = "password123"
        get_user_model().objects.create_user(
            email=test_email,
            password=password
        )
    assert excinfo.value.args[0] == "User must have an email"


def test_create_new_superuser():
    "test creating a new superuser"
    user = get_user_model().objects.create_superuser(
        email="test@super.com",
        password="test"
    )
    assert user.is_superuser
    assert user.is_staff


def test_tag_str():
    """Test the tag string representation"""
    tag = models.Tag.objects.create(
        user=sample_user(),
        name='Vegan'
    )

    assert str(tag) == '<Tag: Vegan>'


def test_ingredients_str():
    """Test the tag string representation"""
    tag = models.Ingredient.objects.create(
        user=sample_user(),
        name='Vegan'
    )

    assert str(tag) == '<Ingredient: Vegan>'

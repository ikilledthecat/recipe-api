import pytest
from django.contrib.auth import get_user_model


pytestmark = pytest.mark.django_db


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

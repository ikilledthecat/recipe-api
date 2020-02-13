from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.core.validators import validate_email
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """Creates and saves a new User"""
        user = self._create_user(email, password, **kwargs)
        user.save(using=self._db)
        return user

    def _create_user(self, email, password=None, **kwargs):
        """Creates a new User"""
        if not email:
            raise AttributeError("User must have an email")
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        """Creates and saves a new super User"""
        user = self._create_user(email, password, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        max_length=255, unique=True, validators=[validate_email]
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Model to be used to store tags for a recipe"""
    name = models.CharField(max_length=255, blank=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"<Tag: {self.name}>"

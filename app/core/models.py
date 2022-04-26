from typing import TYPE_CHECKING
from typing import Any

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import EmailField


class UserManager(
    BaseUserManager["User"] if TYPE_CHECKING else BaseUserManager
):
    def create_user(
        self, email: str, password: str | None = None, **kwargs: Any
    ) -> "User":
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = EmailField(max_length=255, unique=True)
    name = CharField(max_length=255)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

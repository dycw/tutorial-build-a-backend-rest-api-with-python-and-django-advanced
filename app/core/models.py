from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from beartype import beartype
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db.models import CASCADE
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import EmailField
from django.db.models import ForeignKey
from django.db.models import Model


if TYPE_CHECKING:
    _BaseUserManagerUser = BaseUserManager["User"]
else:
    _BaseUserManagerUser = BaseUserManager


class UserManager(_BaseUserManagerUser):
    @beartype
    def create_user(
        self, *, email: str, password: str | None = None, **kwargs: Any
    ) -> "User":
        if email == "":
            raise ValueError(f"{email=}")
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    @beartype
    def create_superuser(self, *, email: str, password: str) -> "User":
        user = self.create_user(email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = cast(str, EmailField(max_length=255, unique=True))
    name = cast(str, CharField(max_length=255))
    is_active = cast(bool, BooleanField(default=True))
    is_staff = cast(bool, BooleanField(default=False))

    objects = UserManager()

    USERNAME_FIELD = "email"


class Tag(Model):
    name = cast(str, CharField(max_length=255))
    user = cast(User, ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE))

    @beartype
    def __str__(self) -> str:
        return self.name


class Ingredient(Model):
    name = cast(str, CharField(max_length=255))
    user = cast(User, ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE))

    @beartype
    def __str__(self) -> str:
        return self.name

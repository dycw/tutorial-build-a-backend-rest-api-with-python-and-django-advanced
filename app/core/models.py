from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from beartype import beartype
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import EmailField


class UserManager(
    BaseUserManager["User"] if TYPE_CHECKING else BaseUserManager
):
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
    email = EmailField(max_length=255, unique=True)
    name = CharField(max_length=255)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    @classmethod
    @beartype
    def get_objects(cls) -> UserManager:
        return cast(UserManager, get_user_model().objects)

import uuid
from pathlib import Path
from typing import Any

from beartype import beartype
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db.models import CASCADE
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import DecimalField
from django.db.models import EmailField
from django.db.models import ForeignKey
from django.db.models import ImageField
from django.db.models import IntegerField
from django.db.models import ManyToManyField
from django.db.models import Model


@beartype
def recipe_image_file_path(_: Any, filename: str) -> str:
    path = Path(filename)
    return Path("uploads", "recipe", f"{uuid.uuid4()}{path.suffix}").as_posix()


class UserManager(BaseUserManager):
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


class Tag(Model):
    name = CharField(max_length=255)
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    @beartype
    def __str__(self) -> str:
        return self.name


class Ingredient(Model):
    name = CharField(max_length=255)
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    @beartype
    def __str__(self) -> str:
        return self.name


class Recipe(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    title = CharField(max_length=255)
    time_minutes = IntegerField()
    price = DecimalField(max_digits=5, decimal_places=2)
    link = CharField(max_length=255, blank=True)
    ingredients = ManyToManyField("Ingredient")
    tags = ManyToManyField("Tag")
    image = ImageField(null=True, upload_to=recipe_image_file_path)

    @beartype
    def __str__(self) -> str:
        return self.title

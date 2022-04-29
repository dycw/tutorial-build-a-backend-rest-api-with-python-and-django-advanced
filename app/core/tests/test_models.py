from typing import cast

from beartype import beartype
from core.models import Ingredient
from core.models import Tag
from core.models import User
from core.models import UserManager
from django.contrib.auth import get_user_model
from django.test import TestCase


@beartype
def sample_user(
    *, email: str = "test@example.com", password: str = "password"
) -> User:
    return cast(UserManager, get_user_model().objects).create_user(
        email=email, password=password
    )


class TestModel(TestCase):
    @beartype
    def test_create_user_with_email_successful(self) -> None:
        email = "test@example.com"
        password = "password"
        user = cast(UserManager, get_user_model().objects).create_user(
            email=email, password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    @beartype
    def test_new_user_email_normalized(self) -> None:
        email = "test@EXAMPLE.COM"
        user = cast(UserManager, get_user_model().objects).create_user(
            email=email, password="password"
        )
        self.assertEqual(user.email, email.lower())

    @beartype
    def test_new_user_invalid_email(self) -> None:
        with self.assertRaises(ValueError):
            _ = cast(UserManager, get_user_model().objects).create_user(
                email="", password="password"
            )

    @beartype
    def test_create_new_superuser(self) -> None:
        user = cast(UserManager, get_user_model().objects).create_superuser(
            email="test@example.com", password="password"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    @beartype
    def test_tag_str(self) -> None:
        tag = Tag.objects.create(user=sample_user(), name="vegan")
        self.assertEqual(str(tag), tag.name)

    @beartype
    def test_ingredient_str(self) -> None:
        ingredient = Ingredient.objects.create(
            user=sample_user(), name="Cucumber"
        )
        self.assertEqual(str(ingredient), ingredient.name)

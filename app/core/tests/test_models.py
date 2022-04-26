from typing import cast

from beartype import beartype
from core.models import UserManager
from django.contrib.auth import get_user_model
from django.test import TestCase


class TestModel(TestCase):
    @beartype
    def test_create_user_with_email_successful(self) -> None:
        email = "test@example.com"
        password = "password"  # noqa: S105
        manager = cast(UserManager, get_user_model().objects)
        user = manager.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    @beartype
    def test_new_user_email_normalized(self) -> None:
        email = "test@EXAMPLE.COM"
        manager = cast(UserManager, get_user_model().objects)
        user = manager.create_user(  # noqa: S106
            email=email, password="password"
        )
        self.assertEqual(user.email, email.lower())

    @beartype
    def test_new_user_invalid_email(self) -> None:
        manager = cast(UserManager, get_user_model().objects)
        with self.assertRaises(ValueError):
            _ = manager.create_user(email="", password="password")  # noqa: S106

    @beartype
    def test_create_new_superuser(self) -> None:
        manager = cast(UserManager, get_user_model().objects)
        user = manager.create_superuser(  # noqa: S106
            email="test@example.com", password="password"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

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
        user = manager.create_user(email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    @beartype
    def test_new_user_email_normalized(self) -> None:
        email = "test@EXAMPLE.COM"
        manager = cast(UserManager, get_user_model().objects)
        user = manager.create_user(email, password="password")  # noqa: S106
        self.assertEqual(user.email, email.lower())

    @beartype
    def test_new_user_invalid_email(self) -> None:
        manager = cast(UserManager, get_user_model().objects)
        with self.assertRaises(ValueError):
            _ = manager.create_user("", password="password")  # noqa: S106

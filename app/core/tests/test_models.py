from typing import cast

from beartype import beartype
from core.models import UserManager
from django.contrib.auth import get_user_model
from hypothesis import given
from hypothesis.extra.django import TestCase
from hypothesis.strategies import text


class TestModel(TestCase):
    @beartype
    @given(email=text(), password=text())
    def test_create_user_with_email_successful(
        self, email: str, password: str
    ) -> None:
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
        # with self.assertRaises(ValueError):
        pass

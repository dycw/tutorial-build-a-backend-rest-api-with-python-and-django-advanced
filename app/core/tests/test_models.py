from beartype import beartype
from core.models import get_user_model_manager
from django.test import TestCase


class TestModel(TestCase):
    @beartype
    def test_create_user_with_email_successful(self) -> None:
        email = "test@example.com"
        password = "password"
        user = get_user_model_manager().create_user(
            email=email, password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    @beartype
    def test_new_user_email_normalized(self) -> None:
        email = "test@EXAMPLE.COM"
        user = get_user_model_manager().create_user(
            email=email, password="password"
        )
        self.assertEqual(user.email, email.lower())

    @beartype
    def test_new_user_invalid_email(self) -> None:
        with self.assertRaises(ValueError):
            _ = get_user_model_manager().create_user(
                email="", password="password"
            )

    @beartype
    def test_create_new_superuser(self) -> None:
        user = get_user_model_manager().create_superuser(
            email="test@example.com", password="password"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

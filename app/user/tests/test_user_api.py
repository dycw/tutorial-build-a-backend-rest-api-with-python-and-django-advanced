from typing import Any
from typing import cast

from beartype import beartype
from core.models import User
from core.models import get_user_model_manager
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient


CREATE_USER_URL = reverse("user:create")


def create_user(**params: Any) -> User:
    return get_user_model_manager().create_user(**params)


class TestPublicUserAPI(TestCase):
    @beartype
    def setUp(self) -> None:
        self.client = APIClient()

    @beartype
    def test_create_valid_user_success(self) -> None:
        password = "password"
        payload = {
            "email": "test@example.com",
            "password": password,
            "name": "Full Name",
        }
        res = cast(Response, self.client.post(CREATE_USER_URL, payload))
        self.assertEqual(res.status_code, HTTP_201_CREATED)
        user = get_user_model_manager().get(**res.data)
        self.assertTrue(user.check_password(password))
        self.assertNotIn(password, res.data)

    @beartype
    def test_user_exists(self) -> None:
        payload = {"email": "test@example.com", "password": "password"}
        _ = create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)

    @beartype
    def test_password_too_short(self) -> None:
        email = "test@example.com"
        payload = {"email": email, "password": "pw"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)
        self.assertFalse(get_user_model_manager().filter(email=email).exists())

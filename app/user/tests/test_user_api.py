from typing import Any
from typing import cast

from beartype import beartype
from core.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.test import APIClient


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params: Any) -> User:
    return User.get_objects().create_user(**params)


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
        user = User.get_objects().get(**res.data)
        self.assertTrue(user.check_password(password))
        self.assertNotIn(password, res.data)

    @beartype
    def test_user_exists(self) -> None:
        payload = {"email": "test@example.com", "password": "password"}
        _ = create_user(**payload)
        res = cast(Response, self.client.post(CREATE_USER_URL, payload))
        self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)

    @beartype
    def test_password_too_short(self) -> None:
        email = "test@example.com"
        payload = {"email": email, "password": "pw", "name": "User name"}
        res = cast(Response, self.client.post(CREATE_USER_URL, payload))
        self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)
        self.assertFalse(User.get_objects().filter(email=email).exists())

    @beartype
    def test_create_token_for_user(self) -> None:
        payload = {"email": "test@example.com", "password": "password"}
        _ = create_user(**payload)
        res = cast(Response, self.client.post(TOKEN_URL, payload))
        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertIn("token", res.data)

    @beartype
    def test_create_token_invalid_credentials(self) -> None:
        email = "test@example.com"
        _ = create_user(email=email, password="password")
        payload = {"email": email, "password": "wrong_password"}
        res = cast(Response, self.client.post(TOKEN_URL, payload))
        self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    @beartype
    def test_create_token_no_user(self) -> None:
        payload = {"email": "test@example.com", "password": "password"}
        res = cast(Response, self.client.post(TOKEN_URL, payload))
        self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    @beartype
    def test_create_token_missing_field(self) -> None:
        payload = {"email": "test@example.com", "password": ""}
        res = cast(Response, self.client.post(TOKEN_URL, payload))
        self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    @beartype
    def test_retrieve_user_unauthorized(self) -> None:
        res = cast(Response, self.client.get(ME_URL))
        self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED)


class TestPrivateUserAPI(TestCase):
    @beartype
    def setUp(self) -> None:
        self.user = create_user(
            email="test@example.com", password="password", name="Full Name"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @beartype
    def test_retrieve_profile_success(self) -> None:
        res = cast(Response, self.client.get(ME_URL))
        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(
            res.data, {"email": self.user.email, "name": self.user.name}
        )

    @beartype
    def test_post_me_not_allowed(self) -> None:
        res = cast(Response, self.client.post(ME_URL, {}))
        self.assertEqual(res.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    @beartype
    def test_update_user_profile(self) -> None:
        password = "new_password"
        name = "New Full Name"
        payload = {"password": password, "name": name}
        res = cast(Response, self.client.patch(ME_URL, payload))
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(self.user.name, name)
        self.assertTrue(self.user.check_password(password))

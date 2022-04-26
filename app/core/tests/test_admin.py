from http import HTTPStatus
from typing import cast

from beartype import beartype
from core.models import UserManager
from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.urls import reverse


class TestAdminSite(TestCase):
    @beartype
    def setUp(self) -> None:
        self.client = Client()
        self.manager = cast(UserManager, get_user_model().objects)
        self.admin_user = self.manager.create_superuser(  # noqa: S106
            email="admin@example.com", password="password"
        )
        self.client.force_login(self.admin_user)
        self.user = self.manager.create_user(  # noqa: S106
            email="test@example.com", password="password", name="Full name"
        )

    @beartype
    def test_users_listed(self) -> None:
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    @beartype
    def test_user_change_page(self) -> None:
        url = reverse("admin:core_user_change", args=[self.user.pk])
        # /admin/core/user/
        res = self.client.get(url)
        self.assertEqual(res.status_code, HTTPStatus.OK)

    @beartype
    def test_create_user_page(self) -> None:
        url = reverse("admin:core_user_add")
        res = self.client.get(url)
        self.assertEqual(res.status_code, HTTPStatus.OK)

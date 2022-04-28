from typing import cast

from beartype import beartype
from core.models import Tag
from core.models import User
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import TagSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.test import APIClient


TAGS_URL = reverse("recipe:tag-list")


class TestPublicTagsAPI(TestCase):
    @beartype
    def setUp(self) -> None:
        self.client = APIClient()

    @beartype
    def test_login_required(self) -> None:
        res = cast(Response, self.client.get(TAGS_URL))
        self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED)


class TestPrivateTagsAPI(TestCase):
    @beartype
    def setUp(self) -> None:
        self.user = User.get_objects().create_user(
            email="test@example.com", password="password"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @beartype
    def test_retrieve_tags(self) -> None:
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")
        res = cast(Response, self.client.get(TAGS_URL))
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    @beartype
    def test_tags_limited_to_user(self) -> None:
        tag = Tag.objects.create(user=self.user, name="Comfort Food")
        user2 = User.get_objects().create_user(
            email="other@example.com", password="password"
        )
        _ = Tag.objects.create(user=user2, name="Fruity")
        res = cast(Response, self.client.get(TAGS_URL))
        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)

    @beartype
    def test_create_tag_successful(self) -> None:
        name = "Test tag"
        payload = {"name": name}
        res = self.client.post(TAGS_URL, payload)
        exists = Tag.objects.filter(user=self.user, name=name).exists()
        self.assertEqual(res.status_code, HTTP_201_CREATED)
        self.assertTrue(exists)

    @beartype
    def test_create_tag_invalid(self) -> None:
        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)

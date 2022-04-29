from typing import cast

from beartype import beartype
from core.models import Recipe
from core.models import User
from core.models import UserManager
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.test import APIClient


RECIPES_URL = reverse("recipe:recipe-list")


@beartype
def sample_recipe(
    user: User,
    *,
    title: str = "Sample recipe",
    time_minutes: int = 10,
    price: float = 5.0,
    link: str = "",
) -> Recipe:
    return Recipe.objects.create(
        user=user,
        title=title,
        time_minutes=time_minutes,
        price=price,
        link=link,
    )


class TestPublicRecipesAPI(TestCase):
    @beartype
    def setUp(self) -> None:
        self.client = APIClient()

    @beartype
    def test_login_required(self) -> None:
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED)


class TestPrivateRecipesAPI(TestCase):
    @beartype
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = cast(UserManager, get_user_model().objects).create_user(
            email="test@example.com", password="password"
        )
        self.client.force_authenticate(self.user)

    @beartype
    def test_retrieve_recipe_list(self) -> None:
        _ = sample_recipe(user=self.user)
        res = cast(Response, self.client.get(RECIPES_URL))
        recipes = Recipe.objects.all().order_by("-id")
        self.assertEqual(res.status_code, HTTP_200_OK)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)

    @beartype
    def test_recipes_limited_to_user(self) -> None:
        _ = sample_recipe(user=self.user, title="Sample recipe 1")
        user2 = cast(UserManager, get_user_model().objects).create_user(
            email="other@example.com", password="password"
        )
        _ = sample_recipe(user=user2, title="Sample recipe 2")
        res = cast(Response, self.client.get(RECIPES_URL))
        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)

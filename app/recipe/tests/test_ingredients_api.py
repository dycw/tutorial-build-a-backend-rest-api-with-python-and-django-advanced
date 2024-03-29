from typing import cast

from beartype import beartype
from core.models import Ingredient
from core.models import Recipe
from core.models import UserManager
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import IngredientSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.test import APIClient


INGREDIENTS_URL = reverse("recipe:ingredient-list")


class TestPublicIngredientsAPI(TestCase):
    @beartype
    def setUp(self) -> None:
        self.client = APIClient()

    @beartype
    def test_login_required(self) -> None:
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED)


class TestPrivateIngredientsAPI(TestCase):
    @beartype
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = cast(UserManager, get_user_model().objects).create_user(
            email="test@example.com", password="password"
        )
        self.client.force_authenticate(self.user)

    @beartype
    def test_retrieve_ingredient_list(self) -> None:
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Salt")
        res = cast(Response, self.client.get(INGREDIENTS_URL))
        ingredients = Ingredient.objects.all().order_by("-name")
        self.assertEqual(res.status_code, HTTP_200_OK)
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    @beartype
    def test_ingredients_limited_to_user(self) -> None:
        Ingredient.objects.create(user=self.user, name="Tumeric")
        user2 = cast(UserManager, get_user_model().objects).create_user(
            email="other@example.com", password="password"
        )
        _ = Ingredient.objects.create(user=user2, name="Vinegar")
        res = cast(Response, self.client.get(INGREDIENTS_URL))
        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        ingredients = Ingredient.objects.filter(user=self.user)
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    @beartype
    def test_create_ingredient_successful(self) -> None:
        name = "Cabbage"
        payload = {"name": name}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, HTTP_201_CREATED)
        self.assertTrue(
            Ingredient.objects.filter(user=self.user, name=name).exists()
        )

    @beartype
    def test_create_ingredient_invalid(self) -> None:
        payload = {"name": ""}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)

    @beartype
    def test_retrieve_ingredients_assigned_to_recipes(self) -> None:
        ingredient1 = Ingredient.objects.create(user=self.user, name="Apples")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Turkey")
        recipe = Recipe.objects.create(
            user=self.user, title="Apple crumble", time_minutes=5, price=10.00
        )
        recipe.ingredients.add(ingredient1)
        res = cast(
            Response, self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        )
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    @beartype
    def test_retrieve_ingredients_assigned_unique(self) -> None:
        ingredient = Ingredient.objects.create(user=self.user, name="Eggs")
        Ingredient.objects.create(user=self.user, name="Cheese")
        recipe1 = Recipe.objects.create(
            user=self.user, title="Eggs benedict", time_minutes=30, price=12.00
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title="Coriander eggs on toast",
            time_minutes=20,
            price=5.00,
        )
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)
        res = cast(
            Response, self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        )
        self.assertEqual(len(res.data), 1)

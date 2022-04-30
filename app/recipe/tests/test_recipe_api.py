from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import cast

from PIL import Image
from beartype import beartype
from core.models import Ingredient
from core.models import Recipe
from core.models import Tag
from core.models import User
from core.models import UserManager
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeDetailSerializer
from recipe.serializers import RecipeSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.test import APIClient


RECIPES_URL = reverse("recipe:recipe-list")
# /api/recipe/recipes/


@beartype
def image_upload_url(pk: int) -> str:
    return reverse("recipe:recipe-upload-image", args=[pk])


@beartype
def detail_url(pk: int) -> str:
    # /api/recipe/recipes/1/
    return reverse("recipe:recipe-detail", args=[pk])


@beartype
def sample_tag(user: User, *, name: str = "Main course") -> Tag:
    return Tag.objects.create(user=user, name=name)


@beartype
def sample_ingredient(user: User, *, name: str = "Cinnamon") -> Ingredient:
    return Ingredient.objects.create(user=user, name=name)


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

    @beartype
    def test_view_recipe_detail(self) -> None:
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        url = detail_url(recipe.pk)
        res = cast(Response, self.client.get(url))
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    @beartype
    def test_create_basic_recipe(self) -> None:
        payload = {
            "title": "Chocolate cheesecake",
            "time_minutes": 30,
            "price": 5.00,
        }
        res = cast(Response, self.client.post(RECIPES_URL, payload))
        self.assertEqual(res.status_code, HTTP_201_CREATED)
        recipe = Recipe.objects.get(pk=res.data["id"])
        for key, value in payload.items():
            self.assertEqual(value, getattr(recipe, key))

    @beartype
    def test_create_recipe_with_tags(self) -> None:
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Dessert")
        payload = {
            "title": "Avocado lime cheesecake",
            "tags": [tag1.pk, tag2.pk],
            "time_minutes": 60,
            "price": 20.00,
        }
        res = cast(Response, self.client.post(RECIPES_URL, payload))
        self.assertEqual(res.status_code, HTTP_201_CREATED)
        recipe = Recipe.objects.get(pk=res.data["id"])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    @beartype
    def test_create_recipe_with_ingredients(self) -> None:
        ingredient1 = sample_ingredient(user=self.user, name="Prawns")
        ingredient2 = sample_ingredient(user=self.user, name="Ginger")
        payload = {
            "title": "Thai prawn red curry",
            "ingredients": [ingredient1.pk, ingredient2.pk],
            "time_minutes": 20,
            "price": 7.00,
        }
        res = cast(Response, self.client.post(RECIPES_URL, payload))
        self.assertEqual(res.status_code, HTTP_201_CREATED)
        recipe = Recipe.objects.get(pk=res.data["id"])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    @beartype
    def test_partial_update_recipe(self) -> None:
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        tag = sample_tag(user=self.user, name="Curry")
        title = "Chicken tikka"
        payload = {"title": title, "tags": [tag.pk]}
        url = detail_url(recipe.pk)
        _ = self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, title)
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(tag, tags)

    @beartype
    def test_full_update_recipe(self) -> None:
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        title = "Spaghetti carbonara"
        time_minutes = 25
        price = 5.00
        payload = {"title": title, "time_minutes": time_minutes, "price": price}
        url = detail_url(recipe.pk)
        _ = self.client.put(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, title)
        self.assertEqual(recipe.time_minutes, time_minutes)
        self.assertEqual(recipe.price, price)
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)

    @beartype
    def test_filter_recipes_by_tags(self) -> None:
        recipe1 = sample_recipe(user=self.user, title="Thai vegetable curry")
        recipe2 = sample_recipe(user=self.user, title="Aubergine with tahini")
        recipe3 = sample_recipe(user=self.user, title="Fish and chips")
        recipe1.tags.add(tag1 := sample_tag(user=self.user, name="Vegan"))
        recipe2.tags.add(tag2 := sample_tag(user=self.user, name="Vegetarian"))
        payload = {"tags": f"{tag1.pk},{tag2.pk}"}
        res = cast(Response, self.client.get(RECIPES_URL, payload))
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    @beartype
    def test_filter_recipes_by_ingredients(self) -> None:
        recipe1 = sample_recipe(user=self.user, title="Posh beans on toast")
        recipe2 = sample_recipe(user=self.user, title="Chicken cacciatore")
        recipe3 = sample_recipe(user=self.user, title="Steak and mushrooms")
        recipe1.ingredients.add(
            ingredient1 := sample_ingredient(user=self.user, name="Feta cheese")
        )
        recipe2.ingredients.add(
            ingredient2 := sample_ingredient(user=self.user, name="Chicken")
        )
        payload = {"ingredients": f"{ingredient1.pk},{ingredient2.pk}"}
        res = cast(Response, self.client.get(RECIPES_URL, payload))
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class TestRecipeImageUpload(TestCase):
    @beartype
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = cast(UserManager, get_user_model().objects).create_user(
            email="test@example.com", password="password"
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    @beartype
    def tearDown(self) -> None:
        self.recipe.image.delete()

    @beartype
    def test_upload_image_to_recipe(self) -> None:
        url = image_upload_url(self.recipe.pk)
        with NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            _ = ntf.seek(0)
            res = cast(
                Response,
                self.client.post(url, {"image": ntf}, format="multipart"),
            )
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(Path(self.recipe.image.path).exists())

    @beartype
    def test_upload_image_bad_request(self) -> None:
        url = image_upload_url(self.recipe.pk)
        res = cast(
            Response,
            self.client.post(url, {"image": "notimage"}, format="multipart"),
        )
        self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)

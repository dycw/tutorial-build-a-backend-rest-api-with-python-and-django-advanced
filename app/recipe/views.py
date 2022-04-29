from typing import cast

from beartype import beartype
from core.models import Ingredient
from core.models import Recipe
from core.models import Tag
from django.db.models.query import QuerySet
from recipe.serializers import IngredientSerializer
from recipe.serializers import RecipeDetailSerializer
from recipe.serializers import RecipeSerializer
from recipe.serializers import TagSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet


class BaseRecipeAttrViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @beartype
    def get_queryset(self) -> QuerySet:
        return (
            cast(QuerySet, self.queryset)
            .filter(user=self.request.user)
            .order_by("-name")
        )

    @beartype
    def perform_create(self, serializer: ModelSerializer) -> None:  # type: ignore
        _ = serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @beartype
    def get_queryset(self) -> QuerySet:
        return cast(QuerySet, self.queryset).filter(user=self.request.user)

    @beartype
    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return RecipeDetailSerializer
        else:
            return cast(type[Serializer], self.serializer_class)

    @beartype
    def perform_create(self, serializer: RecipeSerializer) -> None:  # type: ignore
        _ = serializer.save(user=self.request.user)

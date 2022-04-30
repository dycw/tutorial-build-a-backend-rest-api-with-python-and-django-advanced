from typing import cast

from beartype import beartype
from core.models import Ingredient
from core.models import Recipe
from core.models import Tag
from django.db.models.query import QuerySet
from recipe.serializers import IngredientSerializer
from recipe.serializers import RecipeDetailSerializer
from recipe.serializers import RecipeImageSerializer
from recipe.serializers import RecipeSerializer
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet


class BaseRecipeAttrViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @beartype
    def get_queryset(self) -> QuerySet:
        queryset = cast(QuerySet, self.queryset)
        assigned_only = bool(
            int(self.request.query_params.get("assigned_only", "0"))
        )
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return (
            queryset.filter(user=self.request.user).order_by("-name").distinct()
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
    def _params_to_ints(self, qs: str) -> list[int]:
        return list(map(int, qs.split(",")))

    @beartype
    def get_queryset(self) -> QuerySet:
        query_set = cast(QuerySet, self.queryset).filter(user=self.request.user)
        if (tags := self.request.query_params.get("tags")) is not None:
            query_set = query_set.filter(
                tags__id__in=self._params_to_ints(tags)
            )
        if (
            ingredients := self.request.query_params.get("ingredients")
        ) is not None:
            query_set = query_set.filter(
                ingredients__id__in=self._params_to_ints(ingredients)
            )
        return query_set

    @beartype
    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return RecipeDetailSerializer
        elif self.action == "upload_image":
            return RecipeImageSerializer
        else:
            return cast(type[Serializer], self.serializer_class)

    @beartype
    def perform_create(self, serializer: RecipeSerializer) -> None:  # type: ignore
        _ = serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    @beartype
    def upload_image(
        self, request: Request, pk: str | None = None  # noqa: U100
    ) -> Response:
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

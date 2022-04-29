from typing import TYPE_CHECKING

from core.models import Ingredient
from core.models import Tag
from rest_framework.serializers import ModelSerializer


if TYPE_CHECKING:
    _ModelSerializerTag = ModelSerializer[Tag]
    _ModelSerializerIngredient = ModelSerializer[Ingredient]
else:
    _ModelSerializerTag = _ModelSerializerIngredient = ModelSerializer


class TagSerializer(_ModelSerializerTag):
    class Meta:  # type: ignore
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class IngredientSerializer(_ModelSerializerIngredient):
    class Meta:  # type: ignore
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]

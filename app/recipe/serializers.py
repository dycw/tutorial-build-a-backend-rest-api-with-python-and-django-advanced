from core.models import Ingredient
from core.models import Tag
from rest_framework.serializers import ModelSerializer


class TagSerializer(ModelSerializer):
    class Meta:  # type: ignore
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class IngredientSerializer(ModelSerializer):
    class Meta:  # type: ignore
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]

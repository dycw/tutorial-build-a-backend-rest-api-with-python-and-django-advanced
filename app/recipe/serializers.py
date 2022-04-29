from core.models import Ingredient
from core.models import Recipe
from core.models import Tag
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import PrimaryKeyRelatedField


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


class RecipeSerializer(ModelSerializer):
    ingredients = PrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all()
    )
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:  # type: ignore
        model = Recipe
        fields = [
            "id",
            "title",
            "ingredients",
            "tags",
            "time_minutes",
            "price",
            "link",
        ]
        read_only_fields = ["id"]

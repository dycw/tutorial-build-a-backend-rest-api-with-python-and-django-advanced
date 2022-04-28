from typing import TYPE_CHECKING

from core.models import Tag
from rest_framework.serializers import ModelSerializer


if TYPE_CHECKING:
    _ModelSerializerTag = ModelSerializer[Tag]
else:
    _ModelSerializerTag = ModelSerializer


class TagSerializer(_ModelSerializerTag):
    class Meta:  # type: ignore
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]

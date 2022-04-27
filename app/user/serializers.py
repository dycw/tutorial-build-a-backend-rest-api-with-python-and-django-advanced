from collections.abc import Mapping
from typing import TYPE_CHECKING
from typing import Any

from beartype import beartype
from core.models import User
from core.models import get_user_model_manager
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer


_User = get_user_model()


class UserSerializer(
    ModelSerializer[_User] if TYPE_CHECKING else ModelSerializer
):
    class Meta:  # type: ignore
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    @beartype
    def create(self, validated_data: Mapping[str, Any]) -> User:
        return get_user_model_manager().create_user(**validated_data)

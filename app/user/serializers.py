from collections import OrderedDict
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from beartype import beartype
from core.models import User
from core.models import get_user_model_manager
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy
from rest_framework.serializers import CharField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer
from rest_framework.serializers import ValidationError


_User = get_user_model()


class UserSerializer(
    ModelSerializer[_User] if TYPE_CHECKING else ModelSerializer
):
    class Meta:  # type: ignore
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    @beartype
    def create(self, validated_data: dict[str, Any]) -> User:
        return get_user_model_manager().create_user(**validated_data)

    @beartype
    def update(  # type: ignore
        self, instance: User, validated_data: dict[str, Any]
    ) -> User:
        password = validated_data.pop("password", None)
        user = cast(User, super().update(instance, validated_data))
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(Serializer[Any] if TYPE_CHECKING else Serializer):
    email = CharField()
    password = CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    @beartype
    def validate(self, attrs: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if user is None:
            detail = gettext_lazy(
                "Unable to authenticate with provided credentials"
            )
            raise ValidationError(detail=detail, code="authentication")
        attrs["user"] = user
        return attrs

from typing import cast

from beartype import beartype
from core.models import Tag
from django.db.models.query import QuerySet
from recipe.serializers import TagSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet


class TagViewSet(GenericViewSet, ListModelMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = cast(QuerySet[Tag], Tag.objects.all())
    serializer_class = TagSerializer

    @beartype
    def get_queryset(self) -> QuerySet[Tag]:
        return (
            cast(QuerySet[Tag], self.queryset)
            .filter(user=self.request.user)
            .order_by("-name")
        )

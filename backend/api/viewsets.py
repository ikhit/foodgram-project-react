from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.viewsets import GenericViewSet


class RetrieveListMixin(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    pass


class ListCreateDestroyMixin(
    CreateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet
):
    pass

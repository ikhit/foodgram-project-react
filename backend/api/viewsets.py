from rest_framework.mixins import (
    RetrieveModelMixin,
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
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

from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.viewsets import GenericViewSet


class ListCreateDestroyMixin(
    CreateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet
):
    pass


class RetrieveListMixin(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    pass

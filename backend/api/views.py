from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from .mixins import RetrieveListMixin, ListCreateDestroyMixin
from api.serializers import (
    IngredientsSerializer,
    TagsSerializer,
    RecipesCreateSerializer,
    FollowSerializer,
)
from recipes.models import Follow, Ingredients, Tag, Recipe
from users.models import User


class TagsViewSet(RetrieveListMixin):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class IngredientsViewSet(RetrieveListMixin):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipesCreateSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class FollowViewSet(ListCreateDestroyMixin):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user).annotate(
            recipes_count=Count("following__recipes")
        )

    @action(detail=True, methods=["POST", "DELETE"], url_path="subscribe")
    def follow_unfollow(self, request, pk=None):
        following = get_object_or_404(User, id=self.kwargs["pk"])
        if self.request.method == "DELETE":
            instance = Follow.objects.get(
                user=request.user, following=following
            )
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        context = self.get_serializer_context()
        context["following"] = following
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, following=following)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["GET"])
    def subscribers_list(self, request, pk=None):
        return super().list(request)

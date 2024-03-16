from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .mixins import RetrieveListMixin, ListCreateDestroyMixin
from api.serializers import IngredientsSerializer, TagsSerializer, RecipesCreateSerializer, FollowSerializer
from recipes.models import Ingredients, Tag, Recipe
from users.models import Follow


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
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def get_queryset(self):
        user = self.request.user
        return user.users.all()

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)



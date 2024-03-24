from django.db.models import Count, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from .viewsets import RetrieveListMixin, ListCreateDestroyMixin
from api.serializers import (
    IngredientsSerializer,
    TagsSerializer,
    RecipesCreateSerializer,
    FollowSerializer,
    FavoriteSerializer,
    ShopingCartSerializer,
)
from recipes.models import (
    Favorite,
    Follow,
    Ingredients,
    Tag,
    Recipe,
    ShopingCart,
)
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

    @action(detail=True, methods=["POST", "DELETE"], url_path="favorite")
    def add_or_delete_favorires(self, request, pk=None):
        """Добавление или удаление рецепта из 'избранного'."""
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        if request.method == "POST":
            instance = Favorite.objects.create(
                user=request.user, favorite=recipe
            )
            serializer = FavoriteSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )
        instance = Favorite.objects.get(user=request.user, favorite=recipe)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST", "DELETE"], url_path="shopping_cart")
    def add_or_delete_recipes(self, request, pk=None):
        """Добавить рецепт в корзину или удалить его из корзины."""
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        if request.method == "POST":
            instance = ShopingCart.objects.create(
                user=request.user, shoping_list=recipe
            )
            serializer = ShopingCartSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )
        instance = get_object_or_404(
            ShopingCart, user=request.user, shoping_list=recipe
        )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["GET"], url_path="download_shopping_cart")
    def send_shopping_list(self, request, pk=None):
        """Скачать список ингредиентов и граммовки."""
        recipe_list = ShopingCart.objects.filter(user=request.user)
        list_text = "Список игредиентов и граммовки: \n"
        for recipe in recipe_list:
            data = recipe.recipe.ingredients.values(
                "ingredient__name", "ingredient__measurement_unit"
            ).annotate(amount=Sum("amount"))
            for ingredient in data:
                list_text += (
                    f"{ingredient['ingredient__name']} - "
                    f"{ingredient['amount']} "
                    f"{ingredient['ingredient__measurement_unit']}\n"
                )

        file_name = f"{request.user}_cart_list.txt"
        return FileResponse(list_text, as_attachment=True, filename=file_name)


class FollowViewSet(ListCreateDestroyMixin):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user).annotate(
            recipes_count=Count("following__recipes")
        )

    @action(detail=True, methods=["POST", "DELETE"], url_path="subscribe")
    def follow_unfollow(self, request, pk=None):
        """Подписаться или отписаться от пользователя."""
        following = get_object_or_404(User, id=self.kwargs["pk"])
        if request.method == "DELETE":
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
        """Получить список всех подписок."""
        return super().list(request)

from django.db.models import Count, Sum
from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from .filters import RecipeFilter

from .permissions import IsAuthorOrAdminOrReadOnly, SelfORAdminOrReadOnly
from .viewsets import RetrieveListMixin, ListCreateDestroyMixin
from .serializers import (
    IngredientsSerializer,
    TagsSerializer,
    RecipesCreateSerializer,
    FollowSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
)
from recipes.models import (
    Favorite,
    Follow,
    Ingredients,
    Tags,
    Recipe,
    ShoppingCart,
)
from users.models import User


class CustomUserViewSet(DjoserUserViewSet):
    """Переопределение стандартного вьюсета djoser
    для правильной работы эндпоинта /me/ и
    удаление неиспользующихся эндпоинтов.
    """

    permission_classes = (SelfORAdminOrReadOnly,)

    @action(
        ["get", "put", "patch", "delete"],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        elif request.method == "DELETE":
            return self.destroy(request, *args, **kwargs)

    def activation(self, request, *args, **kwargs):
        return HttpResponseNotFound

    def resend_activation(self, request, *args, **kwargs):
        return HttpResponseNotFound

    def reset_password_confirm(self, request, *args, **kwargs):
        return HttpResponseNotFound

    def reset_password(self, request, *args, **kwargs):
        return HttpResponseNotFound

    def set_username(self, request, *args, **kwargs):
        return HttpResponseNotFound

    def reset_username_confirm(self, request, *args, **kwargs):
        return HttpResponseNotFound

    def reset_username(self, request, *args, **kwargs):
        return HttpResponseNotFound


class TagsViewSet(RetrieveListMixin):
    """Набор представлений для тегов."""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)


class IngredientsViewSet(RetrieveListMixin):
    """Набор представлений для ингредиентов."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class RecipesViewSet(viewsets.ModelViewSet):
    """Набор представления для рецептов, добавления рецептов в
    избранное и добавление в корзину.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipesCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    http_method_names = ["get", "put", "post", "delete"]

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        url_name="favorite",
    )
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

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="shopping_cart",
        url_name="shopping-cart",
    )
    def add_or_delete_recipes_to_cart(self, request, pk=None):
        """Добавить рецепт в корзину или удалить его из корзины."""
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        if request.method == "POST":
            instance = ShoppingCart.objects.create(
                user=request.user, recipe=recipe
            )
            serializer = ShoppingCartSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )
        instance = get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe
        )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["GET"], url_path="download_shopping_cart")
    def send_shopping_list(self, request, pk=None):
        """Скачать список ингредиентов и граммовки."""
        recipe_list = ShoppingCart.objects.filter(user=request.user)
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

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="subscribe",
        url_name="follow",
    )
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
    def subscriptions_list(self, request, pk=None):
        """Получить список всех подписок."""
        return super().list(request)
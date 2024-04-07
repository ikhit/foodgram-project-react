from django.db.models import Count, Sum
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Favorite, Follow, Ingredient, Recipe, ShoppingCart,
                            Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import FoodgramPagination
from .permissions import IsAuthorOrAdminOrReadOnly, SelfORAdminOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientsSerializer, RecipesCreateSerializer,
                          ShoppingCartSerializer, TagsSerializer)
from .viewsets import ListCreateDestroyMixin, RetrieveListMixin


class CustomUserViewSet(DjoserUserViewSet):
    """Переопределение стандартного вьюсета djoser
    для правильной работы эндпоинта /me/ и
    удаление неиспользующихся эндпоинтов.
    """

    pagination_class = FoodgramPagination
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

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)


class IngredientsViewSet(RetrieveListMixin):
    """Набор представлений для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)


class RecipesViewSet(viewsets.ModelViewSet):
    """Набор представления для рецептов, добавления рецептов в
    избранное и добавление в корзину.
    """

    queryset = Recipe.objects.all().order_by("-pub_date")
    serializer_class = RecipesCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = FoodgramPagination
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
        recipe_list = (
            ShoppingCart.objects.filter(user=request.user)
            .values(
                "recipe__ingredients__name",
                "recipe__ingredients__measurement_unit",
            )
            .annotate(amount=Sum("recipe__ingredients__amounts__amount"))
        )
        list_text = "Список игредиентов и граммовки: \n\n"
        for ingredient in recipe_list:
            list_text += (
                f"{ingredient['recipe__ingredients__name']} - "
                f"{ingredient['amount']} "
                f"{ingredient['recipe__ingredients__measurement_unit']};\n"
            )
        response = HttpResponse(list_text, content_type="text/plain")
        response["Content-Disposition"] = "attachment"
        return response


class FollowViewSet(ListCreateDestroyMixin):
    pagination_class = FoodgramPagination
    serializer_class = FollowSerializer

    def get_queryset(self):
        return (
            Follow.objects.filter(user=self.request.user)
            .annotate(recipes_count=Count("following__recipes"))
            .order_by("id")
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

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow, User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import FoodgramPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    CustomUserSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientsSerializer,
    RecipesCreateSerializer,
    ShoppingCartSerializer,
    TagsSerializer,
)


class CustomUserViewSet(DjoserUserViewSet):
    """Переопределение стандартного вьюсета djoser
    для правильной работы эндпоинта /me/ и
    удаление неиспользующихся эндпоинтов.
    """

    pagination_class = FoodgramPagination

    def get_serializer_class(self):
        if self.action == "me" and self.request.method == "GET":
            return CustomUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "me":
            return [
                IsAuthenticated(),
            ]
        return super().get_permissions()

    @action(
        detail=True,
        methods=["POST"],
        url_path="subscribe",
        url_name="follow",
        permission_classes=(IsAuthenticated,),
    )
    def follow(self, request, id=None):
        """Подписаться или отписаться от пользователя."""
        following = get_object_or_404(User, id=self.kwargs["id"])
        context = self.get_serializer_context()
        context["following"] = following
        serializer = FollowSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, following=following)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @follow.mapping.delete
    def delete_follow(self, request, id=None):
        following = get_object_or_404(User, id=self.kwargs["id"])
        delete_cnt, _ = Follow.objects.filter(
            following=following, user=request.user
        ).delete()
        if not delete_cnt:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["GET"],
        url_path="subscriptions",
        permission_classes=(IsAuthenticated,),
        pagination_class=FoodgramPagination,
    )
    def subscriptions_list(self, request, pk=None):
        """Получить список всех подписок."""
        queryset = Follow.objects.filter(user=request.user).order_by("id")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FollowSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        methods=["get"],
        detail=False,
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)

    def activation(self, request, *args, **kwargs):
        return NotImplementedError

    def resend_activation(self, request, *args, **kwargs):
        return NotImplementedError

    def reset_password_confirm(self, request, *args, **kwargs):
        return NotImplementedError

    def set_username(self, request, *args, **kwargs):
        return NotImplementedError

    def reset_username_confirm(self, request, *args, **kwargs):
        return NotImplementedError

    def reset_username(self, request, *args, **kwargs):
        return NotImplementedError


class TagsViewSet(ReadOnlyModelViewSet):
    """Набор представлений для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)
    http_method_names = ("get",)


class IngredientsViewSet(ReadOnlyModelViewSet):
    """Набор представлений для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)
    http_method_names = ("get",)


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

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["POST"],
        url_path="favorite",
        url_name="favorite",
    )
    def favorites(self, request, pk=None):
        """Добавить рецепта в 'избранное'."""
        request.data["recipe"] = self.kwargs["pk"]
        serializer = FavoriteSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @favorites.mapping.delete
    def delete_recipe_from_cart(self, request, pk=None):
        """Удалить рецепта из 'избранного'."""
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        delete_cnt, _ = Favorite.objects.filter(
            recipe=recipe, user=request.user
        ).delete()
        if not delete_cnt:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST"],
        url_path="shopping_cart",
        url_name="shopping-cart",
    )
    def cart(self, request, pk=None):
        """Добавить рецепт в корзину."""
        request.data["recipe"] = self.kwargs["pk"]
        serializer = ShoppingCartSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @cart.mapping.delete
    def delete_cart(self, request, pk=None):
        """Удалить рецепт из корзины."""
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        delete_cnt, _ = ShoppingCart.objects.filter(
            recipe=recipe, user=request.user
        ).delete()
        if not delete_cnt:
            return Response(status=status.HTTP_400_BAD_REQUEST)
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

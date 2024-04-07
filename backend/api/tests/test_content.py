from django.contrib.auth import get_user_model
from django.urls import reverse
from recipes.models import Ingredient, Recipe, Tag
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from ..serializers import RecipesCreateSerializer
from .api_data import (create_content_data, expected_recipe_data,
                       expected_recipe_favorite_data, expected_recipe_id_cart,
                       expected_recipe_id_favorite, expected_user_follow,
                       expected_user_list, user_email)

User = get_user_model()


class TestContent(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username="Пользователь",
            email=user_email,
            first_name="Поль",
            last_name="Зователь",
        )
        cls.author = User.objects.create(
            username="Автор",
            email="author@test.com",
            first_name="Ав",
            last_name="Тор",
        )
        cls.tag = Tag.objects.create(
            name="Обед", slug="lunch", color="#32CD32"
        )
        cls.ingredient_1 = Ingredient.objects.create(
            name="горох", measurement_unit="г"
        )
        cls.ingredient_2 = Ingredient.objects.create(
            name="вроде бы мясо", measurement_unit="г"
        )
        cls.ingredient_3 = Ingredient.objects.create(
            name="вроде бы не мясо", measurement_unit="г"
        )
        create_content_data.update({"tags": [cls.tag.pk]})
        serializer = RecipesCreateSerializer(data=create_content_data)
        serializer.is_valid(raise_exception=True)

        serializer.save(author=cls.author)
        cls.recipe = Recipe.objects.get(name="Плов")

        cls.author_token = Token.objects.create(user=cls.author)
        cls.user_token = Token.objects.create(user=cls.user)

    def test_recipe_detail_content(self):
        """Проверка содержания полей при запросе к конкретному рецепту."""
        url_name = "api:recipes-detail"
        url_kwarg = {"pk": self.recipe.pk}
        fields = (
            "name",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )
        nested_fields = (
            "ingredients",
            "tags",
        )
        with self.subTest(name=url_name):
            url = reverse(url_name, kwargs=url_kwarg)
            response = self.client.get(url)
            self.assertTrue(response.data["image"])
            self.assertDictEqual(
                response.data["author"], expected_recipe_data["author"]
            )
            for field in fields:
                self.assertEqual(
                    response.data[field], expected_recipe_data[field]
                )
            for field in nested_fields:
                self.assertEqual(
                    response.data[field],
                    expected_recipe_data[field],
                )

    def test_user_list(self):
        """Проверка содержания списка пользователей."""
        url_name = "api:users-list"
        with self.subTest(name=url_name):
            url = reverse(url_name)
            response = self.client.get(url)
            for field in ("count", "next", "previous"):
                self.assertEqual(
                    response.data[field], expected_user_list[field]
                )
            self.assertEqual(
                response.data["results"], expected_user_list["results"]
            )

    def test_user_follow_response(self):
        """Проверка ответа при подписке на пользователя."""
        url_name = "api:follow-follow"
        url_kwarg = {"pk": self.author.pk}
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
        )
        recipe_fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        with self.subTest(name=url_name):
            self.client.credentials(
                HTTP_AUTHORIZATION="Token " + self.user_token.key
            )
            url = reverse(url_name, kwargs=url_kwarg)
            response = self.client.post(url)
            for field in fields:
                self.assertEqual(
                    response.data[field], expected_user_follow[field]
                )
            for num, field in enumerate(recipe_fields):
                if field != "image":
                    self.assertEqual(
                        response.data["recipes"][0][field],
                        expected_user_follow["recipes"][0][field],
                    )
            self.assertTrue(response.data["recipes"][0]["image"])

    def test_favorites(self):
        """Проверка добавления рецепта в избранное и
        отображения поля is_favorite в рецепте.
        """
        url_name = "api:recipes-favorite"
        url_kwarg = {"pk": self.recipe.pk}
        with self.subTest(name=url_name):
            self.client.credentials(
                HTTP_AUTHORIZATION="Token " + self.user_token.key
            )
            url = reverse(url_name, kwargs=url_kwarg)
            response = self.client.post(url)
            fields = (
                "id",
                "name",
                "cooking_time",
            )
            self.assertTrue(response.data["image"])
            for field in fields:
                self.assertEqual(
                    response.data[field], expected_recipe_favorite_data[field]
                )
            url_detail = reverse("api:recipes-detail", kwargs=url_kwarg)
            response_detail = self.client.get(url_detail)
            fields = (
                "name",
                "text",
                "cooking_time",
                "is_favorited",
                "is_in_shopping_cart",
            )
            nested_fields = (
                "ingredients",
                "tags",
            )
            for field in fields:
                self.assertEqual(
                    response_detail.data[field],
                    expected_recipe_id_favorite[field],
                )
            for field in nested_fields:
                self.assertEqual(
                    response_detail.data[field],
                    expected_recipe_id_favorite[field],
                )

    def test_shopping_cart(self):
        """Проверка добавления рецепта в список покупок и
        отображения поля is_in_shopping_cart в рецепте.
        """
        url_name = "api:recipes-shopping-cart"
        url_kwarg = {"pk": self.recipe.pk}
        with self.subTest(name=url_name):
            self.client.credentials(
                HTTP_AUTHORIZATION="Token " + self.user_token.key
            )
            url = reverse(url_name, kwargs=url_kwarg)
            response = self.client.post(url)
            fields = (
                "id",
                "name",
                "cooking_time",
            )
            self.assertTrue(response.data["image"])
            for field in fields:
                self.assertEqual(
                    response.data[field], expected_recipe_favorite_data[field]
                )

            url_detail = reverse("api:recipes-detail", kwargs=url_kwarg)
            response_detail = self.client.get(url_detail)
            fields = (
                "name",
                "text",
                "cooking_time",
                "is_favorited",
                "is_in_shopping_cart",
            )
            nested_fields = (
                "ingredients",
                "tags",
            )
            for field in fields:
                self.assertEqual(
                    response_detail.data[field],
                    expected_recipe_id_cart[field],
                )
            for field in nested_fields:
                self.assertEqual(
                    response_detail.data[field],
                    expected_recipe_id_cart[field],
                )

    @classmethod
    def tearDownClass(cls):
        """Метод для удаления файлов, которые создаются при тестах."""
        for recipe in Recipe.objects.all():
            if recipe.image and hasattr(recipe.image, "path"):
                recipe.image.delete(save=False)

        super().tearDownClass()

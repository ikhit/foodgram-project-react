from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class TestRoutes(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username="Пользователь", email="user@test.com"
        )
        cls.author = User.objects.create(
            username="Автор", email="author@test.com"
        )
        cls.tag = Tag.objects.create(name="Обед", slug="lunch")
        cls.ingredient = Ingredient.objects.create(
            name="горох", measurement_unit="г"
        )
        cls.recipe = Recipe.objects.create(
            name="Суп из семи круп",
            text="Сомнительно... но, окэй",
            cooking_time=120,
            author=cls.author,
        )
        cls.token = Token.objects.create(user=cls.user)

    def test_user_list_and_detail_availability_for_anonymous(self):
        """Проверка доступа анонимного пользователя к списку пользователей и
        и информации о конкретном пользователе.
        """
        urls = (
            ("api:users-detail", {"id": self.user.pk}),
            ("api:users-list", None),
        )
        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_me_endpoint(self):
        """Проверка доступности эндпоинта /users/me/."""
        users_statuses = (
            (self.user, HTTPStatus.OK),
            (None, HTTPStatus.UNAUTHORIZED),
        )

        for user, expected_status in users_statuses:
            if user:
                self.client.credentials(
                    HTTP_AUTHORIZATION="Token " + self.token.key
                )
                self.client.force_login(user)
            name = "api:users-me"
            with self.subTest(user=user, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)
                self.client.logout()

    def test_recipe_list_and_detail_availability_for_anonymous(self):
        """Проверка доступа анонимного пользователя к списку рецептов и
        и информации о конкретном рецепте.
        """
        urls = (
            ("api:recipes-detail", {"pk": self.recipe.pk}),
            ("api:recipes-list", None),
        )
        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tags_list_and_detail_availability_for_anonymous(self):
        """Проверка доступа анонимного пользователя к списку тегов и
        и информации о конкретном теге.
        """
        urls = (
            ("api:tags-detail", {"pk": self.tag.pk}),
            ("api:tags-list", None),
        )
        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_ingredient_list_and_detail_availability_for_anonymous(self):
        """Проверка доступа анонимного пользователя к списку ингредиентов и
        и информации о конкретном ингредиенте.
        """
        urls = (
            ("api:ingredients-detail", {"pk": self.ingredient.pk}),
            ("api:ingredients-list", None),
        )
        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_following_list_availability_for_logged_user(self):
        """Проверка доступа авторизованного пользователя к
        списку своих подписок.
        """
        users_statuses = (
            (self.user, HTTPStatus.OK),
            (None, HTTPStatus.UNAUTHORIZED),
        )

        for user, expected_status in users_statuses:
            if user:
                self.client.credentials(
                    HTTP_AUTHORIZATION="Token " + self.token.key
                )
                self.client.force_login(user)
            name = "api:user-subscriptions"
            with self.subTest(user=user, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)
                self.client.logout()

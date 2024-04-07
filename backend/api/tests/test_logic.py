from http import HTTPStatus
import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Follow,
    Favorite,
    ShoppingCart,
)

from .api_data import (
    change_password_data,
    image,
    login_data,
    user_password,
    user_email,
)

User = get_user_model()


class TestLogic(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username="Пользователь",
            email=user_email,
        )
        (cls.user.set_password(user_password),)
        cls.user.save()
        cls.author = User.objects.create(
            username="Автор",
            email="author@test.com",
        )
        cls.tag = Tag.objects.create(name="Обед", slug="lunch", color="#32CD32")
        cls.ingredient_1 = Ingredient.objects.create(name="горох", measurement_unit="г")
        cls.ingredient_2 = Ingredient.objects.create(
            name="вроде бы мясо", measurement_unit="г"
        )
        cls.ingredient_3 = Ingredient.objects.create(
            name="вроде бы не мясо", measurement_unit="г"
        )
        cls.recipe = Recipe.objects.create(
            name="Суп из семи круп",
            text="Сомнительно... но, окэй",
            cooking_time=120,
            author=cls.author,
        )
        cls.author_token = Token.objects.create(user=cls.author)
        cls.user_token = Token.objects.create(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        """Метод для удаления файлов, которые создаются при тестах."""
        for recipe in Recipe.objects.all():
            if recipe.image and hasattr(recipe.image, "path"):
                recipe.image.delete(save=False)
        super().tearDownClass()

    def test_post_recipe_availability_for_anonymous(self):
        """Проверка запрета создания рецепта анонимным пользователем."""
        url_name = "api:recipes-list"
        with self.subTest(name=url_name):
            url = reverse(url_name)
            response = self.client.post(url)
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_author_update_recipe(self):
        """Проверка на возможность редактирования рецепта автором."""
        url_name = "api:recipes-detail"
        updated_data = {
            "ingredients": [
                {"id": self.ingredient_1.id, "amount": 10},
                {"id": self.ingredient_3.id, "amount": 20},
            ],
            "tags": [self.tag.id],
            "image": image,
            "name": "Жареный суп",
            "text": "Доработка рецепта от бати. Берегите обои!",
            "cooking_time": 40,
        }
        json_data = json.dumps(updated_data)
        with self.subTest(user=self.author, name=url_name):
            self.client.credentials(HTTP_AUTHORIZATION="Token " + self.author_token.key)
            url = reverse(url_name, kwargs={"pk": self.recipe.pk})
            response = self.client.put(
                url, data=json_data, content_type="application/json"
            )
            self.recipe.refresh_from_db()
            updated_ingredients = list(
                self.recipe.ingredients.values("id", "amounts__amount")
            )
            expected_ingredients = [
                {
                    "id": ingredient["id"],
                    "amounts__amount": ingredient["amount"],
                }
                for ingredient in updated_data["ingredients"]
            ]
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(1, Recipe.objects.all().count())
            self.assertEqual(self.recipe.name, updated_data["name"])
            self.assertEqual(self.recipe.text, updated_data["text"])
            self.assertEqual(updated_ingredients, expected_ingredients)
            self.assertEqual(self.recipe.cooking_time, updated_data["cooking_time"])

    def test_author_delete_recipe(self):
        """Проверка удаления чужих рецептов."""
        url_name = "api:recipes-detail"
        with self.subTest(user=self.author, name=url_name):
            self.client.credentials(HTTP_AUTHORIZATION="Token " + self.author_token.key)
            url = reverse(url_name, kwargs={"pk": self.recipe.pk})
            response = self.client.delete(url)
            self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
            self.assertEqual(0, Recipe.objects.all().count())

    def test_auth_user_post_recipe(self):
        """Проверка создания рецепта авторизованным пользователем."""
        url_name = "api:recipes-list"
        create_data = {
            "ingredients": [
                {"id": self.ingredient_1.id, "amount": 30},
                {"id": self.ingredient_3.id, "amount": 100},
            ],
            "tags": [self.tag.id],
            "image": image,
            "name": "Плов",
            "text": "Охапка дров и плов готов!",
            "cooking_time": 20,
        }

        json_data = json.dumps(create_data)
        with self.subTest(user=self.user, name=url_name):
            self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token.key)
            url = reverse(url_name)
            response = self.client.post(
                url, data=json_data, content_type="application/json"
            )
            self.assertEqual(response.status_code, HTTPStatus.CREATED)
            self.assertEqual(2, Recipe.objects.all().count())
            self.assertEqual(self.user, Recipe.objects.get(name="Плов").author)

    def test_other_cant_edit_recipe(self):
        """Проверка запрета редактирования чужих рецептов."""
        url_name = "api:recipes-detail"
        updated_data = {
            "ingredients": [
                {"id": self.ingredient_1.id, "amount": 10},
                {"id": self.ingredient_3.id, "amount": 20},
            ],
            "tags": [self.tag.id],
            "image": image,
            "name": "Жареный суп",
            "text": "Доработка рецепта от бати. Берегите обои!",
            "cooking_time": 40,
        }
        json_data = json.dumps(updated_data)
        with self.subTest(user=self.user, name=url_name):
            self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token.key)
            url = reverse(url_name, kwargs={"pk": self.recipe.pk})
            response = self.client.put(
                url, data=json_data, content_type="application/json"
            )
            self.recipe.refresh_from_db()
            recipe_ingredients = list(
                self.recipe.ingredients.values("id", "amounts__amount")
            )
            self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
            self.assertEqual(1, Recipe.objects.all().count())
            self.assertEqual(self.recipe.name, "Суп из семи круп")
            self.assertEqual(self.recipe.text, "Сомнительно... но, окэй")
            self.assertEqual(recipe_ingredients, [])
            self.assertEqual(self.recipe.cooking_time, 120)

    def test_other_cant_delete_recipe(self):
        """Проверка запрета удаления и редактирования чужих рецептов."""
        url_name = "api:recipes-detail"
        with self.subTest(user=self.user, name=url_name):
            self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token.key)
            url = reverse(url_name, kwargs={"pk": self.recipe.pk})
            response = self.client.delete(url)
            self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
            self.assertEqual(1, Recipe.objects.all().count())

    def test_following(self):
        """Проверка на возможность авторизованного пользователя
        подписаться на другого авторизованного пользователя.
        """
        users_statuses = (
            (None, HTTPStatus.UNAUTHORIZED, 0),
            (self.user, HTTPStatus.CREATED, 1),
        )
        for user, expected_status, expected_follows in users_statuses:
            if user:
                self.client.credentials(
                    HTTP_AUTHORIZATION="Token " + self.user_token.key
                )
                self.client.force_login(user)
            name = ("api:follow-follow", {"pk": self.author.pk})
            with self.subTest(user=user, name=name[0]):
                url = reverse(name[0], kwargs=name[1])
                response = self.client.post(url)
                self.assertEqual(response.status_code, expected_status)
                self.assertEqual(expected_follows, Follow.objects.all().count())
                self.client.logout()

    def test_add_recipe_to_shopping_cart(self):
        """Проверка на возможность авторизованного пользователя
        добавить рецепт в корзину.
        """
        users_statuses = (
            (None, HTTPStatus.UNAUTHORIZED, 0),
            (self.user, HTTPStatus.CREATED, 1),
        )
        for user, expected_status, expected_cart in users_statuses:
            if user:
                self.client.credentials(
                    HTTP_AUTHORIZATION="Token " + self.user_token.key
                )
                self.client.force_login(user)
            name = (
                "api:recipes-shopping-cart",
                {"pk": self.recipe.pk},
            )
            with self.subTest(user=user, name=name[0]):
                url = reverse(name[0], kwargs=name[1])
                response = self.client.post(url)
                self.assertEqual(response.status_code, expected_status)
                self.assertEqual(expected_cart, ShoppingCart.objects.all().count())
                self.client.logout()

    def test_add_recipe_to_favorite(self):
        """Проверка на возможность авторизованного пользователя
        добавить рецепт в избранное.
        """
        users_statuses = (
            (None, HTTPStatus.UNAUTHORIZED, 0),
            (self.user, HTTPStatus.CREATED, 1),
        )
        for user, expected_status, expected_favorite in users_statuses:
            if user:
                self.client.credentials(
                    HTTP_AUTHORIZATION="Token " + self.user_token.key
                )
                self.client.force_login(user)
            name = (
                "api:recipes-favorite",
                {"pk": self.recipe.pk},
            )
            with self.subTest(user=user, name=name[0]):
                url = reverse(name[0], kwargs=name[1])
                response = self.client.post(url)
                self.assertEqual(response.status_code, expected_status)
                self.assertEqual(expected_favorite, Favorite.objects.all().count())
                self.client.logout()

    def test_user_set_password(self):
        """Проверка смены пароля."""
        name = "api:users-set-password"
        json_data = json.dumps(change_password_data)
        with self.subTest(user=self.user, name=name):
            self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token.key)
            url = reverse(name)
            response = self.client.post(
                url, data=json_data, content_type="application/json"
            )
            self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_get_auth_token(self):
        """Проверка получения токена."""
        name = "api:login"
        json_data = json.dumps(login_data)
        with self.subTest(name=name):
            url = reverse(name)
            response = self.client.post(
                url, data=json_data, content_type="application/json"
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)

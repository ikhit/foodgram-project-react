from django.db import models
from django.core.validators import MinValueValidator

from users.models import User


COOKING_TIME_MINIMUM = 1
INGREDIENTS_AMOUNT_MIN_VALUE = 1
TAGS_NAME_MAX_LENGTH = 15
TAGS_COLOR_MAX_LENGTH = 16
RECIPE_NAME_MAX_LENGTH = 150
INGREDIENTS_NAME_MAX_LENGTH = 150
INGREDIENTS_MEAS_NAME_MAX_LENGTH = 30


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        "Тег", max_length=TAGS_NAME_MAX_LENGTH, unique=True
    )
    slug = models.SlugField("Слаг", unique=True)
    color = models.CharField(
        "Цвет", max_length=TAGS_COLOR_MAX_LENGTH, unique=True
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Модель ингридиентов."""

    name = models.CharField(
        "Название ингридиента", max_length=INGREDIENTS_AMOUNT_MIN_VALUE
    )
    measurement_unit = models.CharField(
        "Единица измерения количества",
        max_length=INGREDIENTS_MEAS_NAME_MAX_LENGTH,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        "Название рецепта", max_length=RECIPE_NAME_MAX_LENGTH
    )
    text = models.TextField("Описание рецепта")
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления в минутах",
        validators=[MinValueValidator(COOKING_TIME_MINIMUM)],
    )
    image = models.ImageField("Фото блюда", upload_to="recipes/images/")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="автор рецепта",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="тег",
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through="Amount",
        related_name="recipes",
        verbose_name="список и количетсво ингредиентов",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class Amount(models.Model):
    """Модель для количетсва ингрединета в блюде."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="amounts")
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name="ингредиент",
        related_name="amounts",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество ингредиентов",
        validators=[MinValueValidator(INGREDIENTS_AMOUNT_MIN_VALUE)],
    )

    def __str__(self):
        return f"{self.ingredient}: {self.amount}"


class Favorite(models.Model):
    """Модель для избранных рецептов."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites"
    )
    favorite = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )

    class Meta:
        verbose_name = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "favorite"], name="unique_user_favorite"
            )
        ]

    def __str__(self):
        return f"Избранное пользователя {self.user}: {self.favorite}"


class Follow(models.Model):
    """Модель подписчика."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="users"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followings", blank=True
    )

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "following"], name="unique_user_following"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("following")),
                name="user_self_following",
            ),
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.following}"


class ShopingCart(models.Model):
    """Модель продуктовой корзины."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="goods"
    )

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="goods"
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина пользователя {self.user}: {self.recipe}"

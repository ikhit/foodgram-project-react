from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from foodgram.const import (
    COOKING_TIME_MAX,
    COOKING_TIME_MIN,
    INGREDIENTS_AMOUNT_MAX,
    INGREDIENTS_AMOUNT_MIN,
    INGREDIENTS_MEAS_NAME_MAX_LENGTH,
    INGREDIENTS_NAME_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    TAGS_COLOR_MAX_LENGTH,
    TAGS_NAME_MAX_LENGTH,
    TAGS_MAX_SLUG_LENGTH,
)
from users.models import User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        "Тег", max_length=TAGS_NAME_MAX_LENGTH, unique=True
    )
    slug = models.SlugField(
        "Слаг", unique=True, max_length=TAGS_MAX_SLUG_LENGTH
    )
    color = ColorField("Цвет", max_length=TAGS_COLOR_MAX_LENGTH, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиентов."""

    name = models.CharField(
        "Название ингридиента", max_length=INGREDIENTS_NAME_MAX_LENGTH
    )
    measurement_unit = models.CharField(
        "Единица измерения количества",
        max_length=INGREDIENTS_MEAS_NAME_MAX_LENGTH,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient_measurement",
            ),
        ]

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
        validators=[
            MinValueValidator(
                COOKING_TIME_MIN,
                message=f"Минимальное значение - {COOKING_TIME_MIN}.",
            ),
            MaxValueValidator(
                COOKING_TIME_MAX,
                message=f"Максимальное значение - {COOKING_TIME_MIN}.",
            ),
        ],
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
        Ingredient,
        through="Amount",
        related_name="recipes",
        verbose_name="список и количетсво ингредиентов",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class Amount(models.Model):
    """Модель для количетсва ингрединета в блюде."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="amounts"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="ингредиент",
        related_name="amounts",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество ингредиентов",
        validators=[
            MinValueValidator(
                INGREDIENTS_AMOUNT_MIN,
                message=f"Минимальное значение - {INGREDIENTS_AMOUNT_MIN}.",
            ),
            MaxValueValidator(
                INGREDIENTS_AMOUNT_MAX,
                message=f"Максимальное значение - {INGREDIENTS_AMOUNT_MAX}.",
            ),
        ],
    )

    class Meta:
        verbose_name = "Ингредиент и количество"

    def __str__(self):
        return f"{self.ingredient}: {self.amount}"


class UserRecipe(models.Model):
    """Абстрактный родительский класс для моделей избранного и корзины."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        default_related_name = "%(class)ss"


class Favorite(UserRecipe):
    """Модель для избранных рецептов."""

    class Meta(UserRecipe.Meta):
        verbose_name = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_favorite"
            )
        ]

    def __str__(self):
        return f"Избранное пользователя {self.user}: {self.recipe}"


class ShoppingCart(UserRecipe):
    """Модель продуктовой корзины."""

    class Meta(UserRecipe.Meta):
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина пользователя {self.user}: {self.recipe}"

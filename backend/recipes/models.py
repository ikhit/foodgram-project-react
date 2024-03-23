from django.db import models
from django.core.validators import MinValueValidator

from users.models import User


COOKING_TIME_MINIMUM = 1
INGREDIENTS_AMOUNT_MIN_VALUE = 1


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField("Тег", max_length=15, unique=True)
    slug = models.SlugField("Слаг", unique=True)
    color = models.CharField("Цвет", max_length=16, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Модель ингридиентов."""

    name = models.CharField("Название ингридиента", max_length=30)
    measurement_unit = models.CharField(
        "Единица измерения количества", max_length=30
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return self.name


class Amount(models.Model):
    """Модель для количетсва ингрединета в блюде."""

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


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField("Название рецепта", max_length=150)
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
        Amount,
        related_name="recipes",
        verbose_name="список и количетсво ингредиентов",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class Favorites(models.Model):
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

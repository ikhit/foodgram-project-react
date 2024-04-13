from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.const import MAX_LENGTH_FOR_NAME


class User(AbstractUser):
    """Модель пользователя."""

    first_name = models.CharField("Имя", max_length=MAX_LENGTH_FOR_NAME)
    last_name = models.CharField("Фамилия", max_length=MAX_LENGTH_FOR_NAME)
    email = models.EmailField("Электронная почта", unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username", "email"]

    def __str__(self):
        return self.username


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

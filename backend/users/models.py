from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.const import (
    MAX_LENGTH_FOR_EMAIL,
    MAX_LENGTH_FOR_NAME,
    MAX_LENGTH_FOR_ROLE,
    ROLES,
)


class User(AbstractUser):
    """Модель пользователя."""

    password = models.CharField(_('password'), max_length=128)
    first_name = models.CharField("Имя", max_length=MAX_LENGTH_FOR_NAME)
    last_name = models.CharField("Фамилия", max_length=MAX_LENGTH_FOR_NAME)
    email = models.EmailField(
        "Электронная почта", max_length=MAX_LENGTH_FOR_EMAIL, unique=True
    )
    role = models.CharField(
        "Роль", max_length=MAX_LENGTH_FOR_ROLE, choices=ROLES, default="user"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписчика."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="users"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followings"
    )

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "following"], name="unique_user_following"
            ),
            models.CheckConstraint(
                check=models.Q(user=models.F("following")),
                name="user_self_following",
            ),
        ]

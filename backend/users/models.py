from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.const import (
    MAX_LENGTH_FOR_EMAIL,
    MAX_LENGTH_FOR_NAME,
    MAX_LENGTH_FOR_ROLE,
    MAX_USER_PASSWORD_LENGTH,
    ROLES,
)


class User(AbstractUser):
    """Модель пользователя."""

    password = models.CharField(
        _("Пароль"), max_length=MAX_USER_PASSWORD_LENGTH
    )
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
        ordering = ["id"]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == "admin"

from django.contrib import admin

from users.models import User
from recipes.models import Ingredients, Tags, Recipe


class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "measurement_unit",
    )
    search_fields = (
        "id",
        "name",
    )


class TagsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "color",
    )
    search_fields = ("id", "name")


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "text",
        "cooking_time",
        "author",
    )
    search_fields = ("id", "name")


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
    )
    search_fields = ("id", "name")


admin.site.register(User, UserAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredients, IngredientsAdmin)

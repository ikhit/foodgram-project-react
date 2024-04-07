from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)


class TagsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "color",
    )
    search_fields = ("id", "name")


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    search_fields = ("id", "name", "author")
    list_filter = ("author", "tags", "name")

    def favorite_count(self, obj):
        return obj.favorites.count()

    favorite_count.short_description = "Добавлений в избранное: "


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
    )
    search_fields = ("id", "username")
    list_filter = ("email", "username")


admin.site.register(User, UserAdmin)
admin.site.register(Tag, TagsAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientsAdmin)

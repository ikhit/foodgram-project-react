from django.contrib import admin

from .models import Amount, Favorite, Ingredient, Recipe, ShoppingCart, Tag


class AmountInline(admin.TabularInline):
    model = Amount
    extra = 0
    min_num = 1


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 0
    min_num = 1


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

    inlines = [AmountInline, TagInline]

    def favorite_count(self, obj):
        return obj.favorites.count()

    favorite_count.short_description = "Добавлений в избранное: "


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__username", "user__email", "recipe__name")


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__username", "user__email", "recipe__name")


admin.site.register(Tag, TagsAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)

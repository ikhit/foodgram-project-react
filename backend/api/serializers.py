import base64

from django.core.files.base import ContentFile
from djoser.serializers import (UserCreateSerializer, UserSerializer,
                                ValidationError)
from recipes.models import (Amount, Favorite, Follow, Ingredient, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import User

from .pagination import PAGE_SIZE


class CustomUserSerializer(UserSerializer):
    """Сериализатор для чтения данных пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user, following=obj
            ).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователя."""

    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        )


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class Base64ImageField(serializers.ImageField):
    """Сериализатор для изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class AmountRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов и их количества в рецепте."""

    id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = Amount
        fields = ("id", "amount")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update(
            IngredientsSerializer(
                instance=Ingredient.objects.get(pk=instance.ingredient.id)
            ).data
        )
        return representation


class AmountReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтнеия названия и количества ингредиентов."""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )
    amount = serializers.IntegerField()

    class Meta:
        model = Amount
        fields = ("id", "name", "amount", "measurement_unit")


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для продуктовой корзины."""

    name = serializers.CharField(source="recipe.name", read_only=True)
    image = serializers.ImageField(source="recipe.image", read_only=True)
    cooking_time = serializers.IntegerField(
        source="recipe.cooking_time", read_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = ("id", "name", "image", "cooking_time")


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов."""

    name = serializers.CharField(source="favorite.name", read_only=True)
    image = serializers.ImageField(source="favorite.image", read_only=True)
    cooking_time = serializers.IntegerField(
        source="favorite.cooking_time", read_only=True
    )

    class Meta:
        model = Favorite
        fields = ("id", "name", "image", "cooking_time")


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода данных о рецепте."""

    image = Base64ImageField()
    author = CustomUserCreateSerializer()
    tags = TagsSerializer(many=True)
    ingredients = AmountReadSerializer(source="amounts", many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "is_favorited",
            "is_in_shopping_cart",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, favorite=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False


class RecipesCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, required=True, queryset=Tag.objects.all()
    )
    ingredients = AmountRecipeSerializer(many=True, required=True)

    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )

    def add_update_ingredients_and_tags(self, ingredients, tags, instance):
        """Добавить или обновить рецепты и теги к рецепту."""
        amounts = [
            Amount(
                recipe=instance,
                ingredient_id=ingredient["id"],
                amount=ingredient["amount"],
            )
            for ingredient in ingredients
        ]
        Amount.objects.bulk_create(amounts)
        instance.tags.set(tags)
        return instance

    def create(self, validated_data):
        ingredient_data = validated_data.pop("ingredients")
        tag_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        return self.add_update_ingredients_and_tags(
            ingredients=ingredient_data, tags=tag_data, instance=recipe
        )

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.image = validated_data.get("image", instance.image)
        tag_data = validated_data.pop("tags")
        ingredient_data = validated_data.pop("ingredients")
        instance.ingredients.all().delete()
        instance = self.add_update_ingredients_and_tags(
            ingredients=ingredient_data, tags=tag_data, instance=instance
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance=instance, context=self.context
        ).data


class FollowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов пользователей
    на которых подписались.
    """

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    recipes = FollowRecipeSerializer(
        source="following.recipes", many=True, read_only=True
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ("following", "recipes", "recipes_count")

    def get_recipes_count(self, instance):
        return instance.following.recipes.count()

    def validate(self, attrs):
        following = self.context.get("following")
        request = self.context.get("request")
        if following == request.user:
            raise ValidationError("Нельзя подписаться на самого себя!")
        if Follow.objects.filter(
            user=request.user, following=following
        ).exists():
            raise ValidationError(
                f"Вы уже подписаны на пользователя {following}."
            )
        return super().validate(attrs)

    def to_representation(self, instance):
        representation = CustomUserSerializer(
            instance=instance.following, context=self.context
        ).data
        representation["recipes"] = FollowRecipeSerializer(
            instance.following.recipes.order_by("-pub_date")[:PAGE_SIZE],
            many=True,
            context=self.context,
        ).data
        representation["recipes_count"] = self.get_recipes_count(instance)
        return representation

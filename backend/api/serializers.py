from djoser.serializers import UserSerializer, ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Amount,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User


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
        return (
            request
            and request.user.is_authenticated
            and Follow.objects.filter(
                user=request.user, following=obj
            ).exists()
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


class AmountRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов и их количества в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all(), write_only=True
    )

    class Meta:
        model = Amount
        fields = ("id", "amount")


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


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода данных о рецепте."""

    image = Base64ImageField()
    author = CustomUserSerializer()
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
        return (
            request
            and request.user.is_authenticated
            and Favorite.objects.filter(user=request.user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )


class RecipesCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, required=True, queryset=Tag.objects.all()
    )
    ingredients = AmountRecipeSerializer(many=True, required=True)

    author = serializers.SlugRelatedField(
        slug_field="username",
        default=serializers.CurrentUserDefault(),
        read_only=True,
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

    def validate(self, data):
        image = data.get("image")
        if not image:
            raise serializers.ValidationError(
                "Изображение рецепта обязательно!"
            )
        tags = data.get("tags")
        if not tags:
            raise serializers.ValidationError(
                "Нельзя создать рецепт без тегов!"
            )
        tag_ids = [tag_id for tag_id in tags]
        if len(set(tag_ids)) != len(tag_ids):
            raise serializers.ValidationError(
                "В рецепте не должно быть одинаковых тегов!"
            )

        ingredients = data.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError(
                "Нельзя создать рецепт без ингредиентов!"
            )
        ingredient_ids = [
            ingredient["ingredient"].id for ingredient in ingredients
        ]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError(
                "В рецепте не должно быть одинаковых ингредиентов!"
            )
        return data

    @staticmethod
    def add_update_ingredients_and_tags(ingredients, tags, instance):
        """Добавить или обновить рецепты и теги к рецепту."""
        for ingredient in ingredients:
            Amount.objects.update_or_create(
                recipe=instance,
                ingredient_id=ingredient["ingredient"].id,
                amount=ingredient["amount"],
            )
        instance.tags.set(tags)

    def create(self, validated_data):
        request = self.context.get("request")
        ingredient_data = validated_data.pop("ingredients")
        tag_data = validated_data.pop("tags")
        validated_data["author"] = request.user
        recipe = Recipe.objects.create(**validated_data)
        self.add_update_ingredients_and_tags(
            ingredients=ingredient_data, tags=tag_data, instance=recipe
        )
        return recipe

    def update(self, instance, validated_data):
        tag_data = validated_data.pop("tags")
        ingredient_data = validated_data.pop("ingredients")
        instance.ingredients.clear()
        self.add_update_ingredients_and_tags(
            ingredients=ingredient_data,
            tags=tag_data,
            instance=instance,
        )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance=instance, context=self.context
        ).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для рецептов.
    Обрабатывает поля id, name, image, cooking_time.
    """

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class FollowerReadSerializer(CustomUserSerializer):
    """Сериализатор для отображения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        model = User
        fields = CustomUserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, instance):
        return instance.recipes.count()

    def get_recipes(self, instance):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        limit_value = int(limit) if limit and limit.isdigit() else None
        return RecipeShortSerializer(
            instance.recipes.order_by("-pub_date")[:limit_value],
            many=True,
            context=self.context,
        ).data


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    user = serializers.SlugRelatedField(
        slug_field="username",
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )

    class Meta:
        model = Follow
        fields = ("following", "user")

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
        return FollowerReadSerializer(
            instance=instance.following, context=self.context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для продуктовой корзины."""

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.SlugRelatedField(
        slug_field="username",
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )

    class Meta:
        model = ShoppingCart
        fields = ("recipe", "user")

    def validate_recipe(self, value):
        request = self.context.get("request")
        user = request.user
        if ShoppingCart.objects.filter(user=user, recipe=value).exists():
            raise serializers.ValidationError("Рецепт уже добавлен в коризну.")
        return value

    def to_representation(self, instance):
        return RecipeShortSerializer(instance=instance.recipe).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в избранное."""

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.SlugRelatedField(
        slug_field="username",
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )

    class Meta:
        model = Favorite
        fields = ("recipe", "user")

    def validate_recipe(self, value):
        request = self.context.get("request")
        user = request.user
        if Favorite.objects.filter(user=user, recipe=value).exists():
            raise serializers.ValidationError(
                "Рецепт уже добавлен в избранное."
            )
        return value

    def to_representation(self, instance):
        return RecipeShortSerializer(instance=instance.recipe).data

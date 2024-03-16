import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from recipes.models import Amount, Ingredients, Tag, Recipe
from users.models import User


class FollowSerializer(serializers.ModelSerializer):
    pass

class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        )


class CustomUserCreateSerializer(UserCreateSerializer):
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

    def validate_username(self, value):
        if value == "me":
            raise serializers.ValidationError(
                "Нельзя использовать 'me' в качестве username!"
            )
        return value


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ("id", "name", "measurement_unit")


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class AmountRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = Amount
        fields = ("id", "amount")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update(
            IngredientsSerializer(
                instance=Ingredients.objects.get(pk=instance.ingredient.id)
            ).data
        )
        return representation


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    author = CustomUserCreateSerializer()
    tags = TagsSerializer(many=True)
    ingredients = AmountRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )


class RecipesCreateSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        ingredient_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredient_data:
            ingredient_id = ingredient.get("id")
            ingredient_amount = ingredient.get("amount")
            ingredient_obj = Ingredients.objects.get(id=ingredient_id)
            ingredients = Amount.objects.create(
                ingredient=ingredient_obj, amount=ingredient_amount
            )
            recipe.ingredients.add(ingredients)

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags")
        if tags_data:
            instance.tags.set(tags_data)
        ingredient_data = validated_data.pop("ingredients")
        if ingredient_data:
            instance.ingredients.all().delete()
            for ingredient in ingredient_data:

                ingredient_id = ingredient.get("id")
                ingredient_amount = ingredient.get("amount")
                ingredient_obj = Ingredients.objects.get(id=ingredient_id)
                ingredients = Amount.objects.create(
                    ingredient=ingredient_obj, amount=ingredient_amount
                )
                instance.ingredients.add(ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance=instance).data

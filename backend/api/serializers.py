import base64
import uuid
import re
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (
    Ingredient, Tag, Recipe, RecipeIngredient,
    ShortLink
)
from users.models import User
from django.conf import settings


class Base64ImageField(serializers.ImageField):
    """Поле для обработки изображений в формате Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str):
            if not data.strip():
                raise serializers.ValidationError(
                    'Изображение не может быть пустым.'
                )
            if data.startswith('data:image'):
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'{uuid.uuid4()}.{ext}'
                )
        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )

    def validate_username(self, value):
        """Валидация username по регулярному выражению."""
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Username может содержать только буквы, цифры и символы '
                '@/./+/-/_'
            )
        return value


class CustomUserSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.follower.filter(author=obj).exists()
        return False


class SetAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для установки аватара."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""

    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверяет, находится ли рецепт в избранном."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.favorites.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, находится ли рецепт в списке покупок."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.shopping_cart.filter(recipe=obj).exists()
        return False


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиента в рецепте."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=settings.MIN_INGREDIENT_AMOUNT,
        max_value=settings.MAX_INGREDIENT_AMOUNT,
        error_messages={
            'min_value': f'Количество должно быть не менее {settings.MIN_INGREDIENT_AMOUNT}.',
            'max_value': f'Количество должно быть не более {settings.MAX_INGREDIENT_AMOUNT}.',
        }
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=False
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=settings.MIN_COOKING_TIME,
        max_value=settings.MAX_COOKING_TIME,
        error_messages={
            'min_value': f'Время приготовления должно быть не менее {settings.MIN_COOKING_TIME} минуты.',
            'max_value': f'Время приготовления должно быть не более {settings.MAX_COOKING_TIME} минут.',
        }
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def validate_ingredients(self, value):
        """Валидация ингредиентов."""
        if not value:
            raise serializers.ValidationError(
                'Нужен хотя бы один ингредиент.'
            )

        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )

        for item in value:
            if not Ingredient.objects.filter(id=item['id']).exists():
                raise serializers.ValidationError(
                    f'Ингредиент с id {item["id"]} не существует.'
                )

        return value

    def validate_tags(self, value):
        """Валидация тегов."""
        if value and len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )

        return value


    def validate_name(self, value):
        """Валидация названия рецепта."""
        if value is None or not str(value).strip():
            raise serializers.ValidationError(
                'Название рецепта не может быть пустым.'
            )
        return value

    def validate_text(self, value):
        """Валидация описания рецепта."""
        if value is None or not str(value).strip():
            raise serializers.ValidationError(
                'Описание рецепта не может быть пустым.'
            )
        return value

    def validate(self, data):
        """Общая валидация данных рецепта."""
        if self.instance:
            if 'ingredients' not in data:
                raise serializers.ValidationError({
                    'ingredients': 'Это поле обязательно.'
                })
            if not data['ingredients']:
                raise serializers.ValidationError({
                    'ingredients': 'Нужен хотя бы один ингредиент.'
                })
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Создание рецепта."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags', [])

        recipe = Recipe.objects.create(**validated_data)
        if tags_data:
            recipe.tags.set(tags_data)

        self._create_ingredients(recipe, ingredients_data)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновление рецепта."""
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._create_ingredients(instance, ingredients_data)

        return super().update(instance, validated_data)

    def _create_ingredients(self, recipe, ingredients_data):
        """Создание ингредиентов для рецепта."""
        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def to_representation(self, instance):
        """Возвращает представление созданного рецепта."""
        return RecipeListSerializer(
            instance, context=self.context
        ).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого представления рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(CustomUserSerializer):
    """Сериализатор пользователя с рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, obj):
        """Возвращает рецепты пользователя."""
        request = self.context.get('request')
        recipes_limit = None

        if request:
            recipes_limit = request.query_params.get('recipes_limit')

        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass

        return RecipeMinifiedSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов пользователя."""
        return obj.recipes.count()


class ShortLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для короткой ссылки."""

    short_link = serializers.SerializerMethodField()

    class Meta:
        model = ShortLink
        fields = ('short_link',)

    def to_representation(self, instance):
        """Переименовываем поле согласно спецификации API."""
        data = super().to_representation(instance)
        data['short-link'] = data.pop('short_link')
        return data

    def get_short_link(self, obj):
        """Возвращает полную короткую ссылку."""
        request = self.context.get('request')
        if request:
            domain = request.get_host()
            protocol = 'https' if request.is_secure() else 'http'
            return f'{protocol}://{domain}/s/{obj.short_code}'
        return f'/s/{obj.short_code}'

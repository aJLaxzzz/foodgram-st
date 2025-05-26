from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Ingredient, Tag, Recipe, RecipeIngredient,
    Favorite, ShoppingCart, ShortLink
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для тегов."""

    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для ингредиентов в рецепте."""

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов."""

    list_display = (
        'id', 'name', 'author', 'cooking_time',
        'get_favorites_count', 'get_image'
    )
    list_filter = ('author', 'tags', 'pub_date')
    search_fields = ('name', 'author__username')
    readonly_fields = ('pub_date', 'get_favorites_count', 'get_image')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)

    def get_favorites_count(self, obj):
        """Возвращает количество добавлений в избранное."""
        return obj.favorites.count()
    get_favorites_count.short_description = 'В избранном'

    def get_image(self, obj):
        """Возвращает миниатюру изображения."""
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="50" height="50" />'
            )
        return 'Нет изображения'
    get_image.short_description = 'Изображение'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов в рецепте."""

    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для избранного."""

    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для списка покупок."""

    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    """Админка для коротких ссылок."""

    list_display = ('id', 'recipe', 'short_code')
    readonly_fields = ('short_code',)

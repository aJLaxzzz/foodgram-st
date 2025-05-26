import django_filters
from recipes.models import Recipe, Ingredient


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов."""

    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    author = django_filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author']

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр по избранным рецептам."""
        if not self.request.user.is_authenticated:
            # Для неаутентифицированных пользователей возвращаем пустой
            # queryset
            if value == 1:
                return queryset.none()
            else:
                return queryset

        if value == 1:
            return queryset.filter(favorites__user=self.request.user)
        elif value == 0:
            return queryset.exclude(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр по рецептам в списке покупок."""
        if value == 1 and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        elif value == 0 and self.request.user.is_authenticated:
            return queryset.exclude(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для ингредиентов."""

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']

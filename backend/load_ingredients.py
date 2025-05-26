#!/usr/bin/env python
"""
Скрипт для загрузки ингредиентов из JSON файла.
"""
import os
import sys
import json
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

from recipes.models import Ingredient


def load_ingredients():
    """Загрузка ингредиентов из JSON файла."""
    print("Загрузка ингредиентов...")

    # Путь к файлу с ингредиентами
    ingredients_file = '/data/ingredients.json'

    if not os.path.exists(ingredients_file):
        print(f"Файл {ingredients_file} не найден")
        return

    try:
        with open(ingredients_file, 'r', encoding='utf-8') as f:
            ingredients_data = json.load(f)

        # Очищаем существующие ингредиенты
        Ingredient.objects.all().delete()

        # Загружаем новые ингредиенты
        ingredients_to_create = []
        for item in ingredients_data:
            ingredient = Ingredient(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
            ingredients_to_create.append(ingredient)

        # Массовое создание для ускорения
        Ingredient.objects.bulk_create(ingredients_to_create, batch_size=1000)

        print(f"Загружено {len(ingredients_to_create)} ингредиентов")

    except Exception as e:
        print(f"Ошибка при загрузке ингредиентов: {e}")
        sys.exit(1)


if __name__ == '__main__':
    load_ingredients()

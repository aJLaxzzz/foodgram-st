#!/usr/bin/env python
"""
Скрипт для загрузки тестовых данных в базу данных.
"""
import os
import sys
import django
from django.core.files import File
from django.conf import settings

# Настройка Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

from django.contrib.auth import get_user_model
from recipes.models import Tag, Recipe, Ingredient, RecipeIngredient
from django.core.files.storage import default_storage

User = get_user_model()

# Данные для рецептов с правильными ингредиентами из CSV
RECIPE_DATA = [
    {
        "name": "Борщ",
        "author_email": "admin@example.com",
        "text": "Традиционный борщ с мясом и овощами. Наваристый, ароматный суп с характерным красным цветом от свеклы. Подается со сметаной и зеленью.",
        "cooking_time": 120,
        "image_path": "recipes/images/borsh.jpg",
        "tags": ["Обед", "Ужин"],
        "ingredients": [
            {"name": "говядина", "amount": 500},
            {"name": "свекла", "amount": 200},
            {"name": "морковь", "amount": 150},
            {"name": "лук репчатый", "amount": 100},
            {"name": "сметана", "amount": 100},
            {"name": "зелень", "amount": 30},
            {"name": "соль", "amount": 5},
        ],
    },
    {
        "name": "Блины классические",
        "author_email": "user@example.com",
        "text": "Классические тонкие блины на молоке. Идеальны для завтрака или десерта. Подавать можно с медом, вареньем, сметаной или любой другой начинкой по вкусу.",
        "cooking_time": 30,
        "image_path": "recipes/images/blini.jpg",
        "tags": ["Завтрак", "Десерт"],
        "ingredients": [
            {"name": "мука", "amount": 200},
            {"name": "молоко", "amount": 500},
            {"name": "яйца куриные", "amount": 2},
            {"name": "сахар", "amount": 50},
            {"name": "соль", "amount": 2},
            {"name": "сливочное масло", "amount": 30},
        ],
    },
]

def create_users():
    """Создание пользователей"""
    print("Создание пользователей...")

    # Создание администратора
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Админ',
            'last_name': 'Администратор',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin.set_password('admin')
        admin.save()
        print("Создан администратор: admin/admin")
    else:
        print("Администратор уже существует")

    # Создание обычного пользователя
    user, created = User.objects.get_or_create(
        username='user',
        defaults={
            'email': 'user@example.com',
            'first_name': 'Тест',
            'last_name': 'Пользователь',
        }
    )
    if created:
        user.set_password('user')
        user.save()
        print("Создан пользователь: user/user")
    else:
        print("Пользователь уже существует")

def create_tags():
    """Создание тегов"""
    print("Создание тегов...")

    tags_data = [
        {'name': 'Завтрак', 'slug': 'breakfast'},
        {'name': 'Обед', 'slug': 'lunch'},
        {'name': 'Ужин', 'slug': 'dinner'},
        {'name': 'Десерт', 'slug': 'dessert'},
        {'name': 'Быстро', 'slug': 'fast'},
    ]

    for tag_data in tags_data:
        tag, created = Tag.objects.get_or_create(
            slug=tag_data['slug'],
            defaults=tag_data
        )
        if created:
            print(f"Создан тег: {tag.name}")
        else:
            print(f"Тег уже существует: {tag.name}")

def create_recipes():
    """Создание рецептов"""
    print("Создание рецептов...")

    for recipe_data in RECIPE_DATA:
        # Проверяем, существует ли рецепт
        if Recipe.objects.filter(name=recipe_data['name']).exists():
            print(f"Рецепт '{recipe_data['name']}' уже существует")
            continue

        # Получаем автора
        try:
            author = User.objects.get(email=recipe_data['author_email'])
        except User.DoesNotExist:
            print(f"Автор с email {recipe_data['author_email']} не найден")
            continue

        # Создаем рецепт
        recipe = Recipe.objects.create(
            name=recipe_data['name'],
            author=author,
            text=recipe_data['text'],
            cooking_time=recipe_data['cooking_time'],
        )

        # Добавляем изображение
        image_path = f"/app/images/{recipe_data['image_path'].split('/')[-1]}"
        if os.path.exists(image_path):
            with open(image_path, 'rb') as img_file:
                recipe.image.save(
                    recipe_data['image_path'].split('/')[-1],
                    File(img_file),
                    save=True
                )

        # Добавляем теги
        for tag_name in recipe_data['tags']:
            try:
                tag = Tag.objects.get(name=tag_name)
                recipe.tags.add(tag)
            except Tag.DoesNotExist:
                print(f"Тег '{tag_name}' не найден")

        # Добавляем ингредиенты
        for ingredient_data in recipe_data['ingredients']:
            try:
                ingredient = Ingredient.objects.get(name=ingredient_data['name'])
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )
            except Ingredient.DoesNotExist:
                print(f"Ингредиент '{ingredient_data['name']}' не найден в базе данных")

        print(f"Создан рецепт: {recipe.name}")

def main():
    """Основная функция загрузки данных"""
    print("=== НАЧАЛО ЗАГРУЗКИ ТЕСТОВЫХ ДАННЫХ ===")

    try:
        create_users()
        create_tags()
        create_recipes()
        print("=== ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО ===")
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для загрузки ингредиентов из CSV файла."""

    help = 'Загрузка ингредиентов из CSV файла'

    def handle(self, *args, **options):
        # Путь к файлу с ингредиентами
        csv_file_path = os.path.join(
            settings.BASE_DIR.parent, 'data', 'ingredients.csv'
        )

        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f'Файл {csv_file_path} не найден')
            )
            return

        # Очищаем существующие ингредиенты
        Ingredient.objects.all().delete()

        ingredients_to_create = []

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    name, measurement_unit = row[0], row[1]
                    ingredients_to_create.append(
                        Ingredient(
                            name=name,
                            measurement_unit=measurement_unit
                        )
                    )

        # Массовое создание ингредиентов
        Ingredient.objects.bulk_create(ingredients_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно загружено {len(ingredients_to_create)} ингредиентов'
            )
        )

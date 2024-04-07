import csv

from django.core.management import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = "Import ingredietns and tags to database."

    def handle(self, *args, **options):
        new_ingredients = []
        with open(
            "data/ingredients.csv", "r", encoding="utf-8"
        ) as ingredients_file:
            reader = csv.reader(ingredients_file)
            existing_names = set(
                Ingredient.objects.all().values_list("name", flat=True)
            )
            for row in reader:
                name, measurement_unit = row
                if name.strip() not in existing_names:
                    new_ingredients.append(
                        Ingredient(
                            name=name.strip(),
                            measurement_unit=measurement_unit.strip(),
                        )
                    )

        Ingredient.objects.bulk_create(new_ingredients, ignore_conflicts=True)

        with open("data/tags.csv", "r", encoding="utf-8") as tags_file:
            reader = csv.reader(tags_file)
            for row in reader:
                name, color, slug = row
                Tag.objects.get_or_create(
                    name=name.strip(),
                    color=color.strip(),
                    slug=slug.strip(),
                )

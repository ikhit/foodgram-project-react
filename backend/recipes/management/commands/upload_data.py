import csv

from django.core.management import BaseCommand

from recipes.models import Ingredients, Tags


class Command(BaseCommand):
    help = "Import ingredietns and tags to database."

    def handle(self, *args, **options):
        with open(
            "../data/ingredients.csv", "r", encoding="utf-8"
        ) as ingredients_file:
            reader = csv.reader(ingredients_file)
            for row in reader:
                name, measurement_unit = row
                Ingredients.objects.get_or_create(
                    name=name.strip(),
                    measurement_unit=measurement_unit.strip(),
                )

        with open("../data/tags.csv", "r", encoding="utf-8") as tags_file:
            reader = csv.reader(tags_file)
            for row in reader:
                name, color, slug = row
                Tags.objects.get_or_create(
                    name=name.strip(),
                    color=color.strip(),
                    slug=slug.strip(),
                )

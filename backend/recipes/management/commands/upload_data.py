import sqlite3

from django.core.management import BaseCommand
import pandas as pd

class Command(BaseCommand):
    help = "Import ingredietns and tags to database."
    
    def handle(self, *args, **options):
        df = pd.read_csv("../data/ingredients.csv")
        df.columns = df.columns.str.strip()
        df.columns = ["name", "measurement_unit"]
        df.index = df.index + 1
        df.index.name = "id"
        connection = sqlite3.connect("db.sqlite3")
        df.to_sql("recipes_ingredients", connection, if_exists="append")
        connection.close()

        df_tags = pd.read_csv("../data/tags.csv")
        connection = sqlite3.connect("db.sqlite3")
        df_tags.to_sql("recipes_tags", connection, if_exists="append", index=False)
        print("Upload done!")
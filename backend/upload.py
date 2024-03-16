import sqlite3

import pandas as pd

df = pd.read_csv("../data/ingredients.csv")
df.columns = df.columns.str.strip()
df.columns = ["name", "measurement_unit"]
df.index = df.index + 1
df.index.name = "id"
connection = sqlite3.connect("db.sqlite3")
df.to_sql("recipes_ingredients", connection, if_exists="append")
connection.close()

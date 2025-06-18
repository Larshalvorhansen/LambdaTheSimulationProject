import pandas as pd
import sqlite3
from rich import print
from rich.console import Console
from rich.traceback import install

# Better error handling:
install()
console = Console()


url = "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Population%20(OWID%20based)/Population%20(OWID%20based).csv"

df = pd.read_csv(url)

conn = sqlite3.connect("owid_data.db")

df.to_sql("population", conn, if_exists="replace", index=False)

sample = pd.read_sql("SELECT * FROM population LIMIT 5;", conn)
print(sample)


conn.close()

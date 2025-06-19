import pandas as pd
import sqlite3
from rich import print
from rich.console import Console
from rich.traceback import install

# Better error handling:
install()
console = Console()


# Use a super simple and reliable CSV URL
url = "https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv"

# Load the CSV
df = pd.read_csv(url)

# Print a sample
print(df.head())

# Save to SQLite
conn = sqlite3.connect("data.db")
df.to_sql("simple_table", conn, if_exists="replace", index=False)
conn.close()
print("Done")


conn.close()

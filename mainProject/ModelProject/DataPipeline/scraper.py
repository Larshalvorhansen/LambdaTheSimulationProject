import pandas as pd
import sqlite3
from rich import print
from rich.console import Console
from rich.traceback import install

install()
console = Console()

# print("[bold green]GDP data saved to econ.db[/bold green]")

# raise ValueError("Oops! Something went wrong")
# Step 1: Fetch CSV data from OWID
csv_url = "https://ourworldindata.org/grapher/population-growth-rates.csv"
df = pd.read_csv(csv_url)

# Step 2: Clean and rename columns
df = df.rename(columns={"Population growth rate": "pop_growth_pct"})

# Step 3: Optional filter – only keep global data
world_df = df[df["Entity"] == "World"]

# Step 4: Save to SQLite database
conn = sqlite3.connect("owid_population.db")

# Save full dataset
df.to_sql("pop_growth", conn, if_exists="replace", index=False)

# Save filtered dataset
world_df.to_sql("pop_growth_world", conn, if_exists="replace", index=False)

conn.close()

# Step 5: Re-open and query recent world data (optional)
conn = sqlite3.connect("owid_population.db")
recent = pd.read_sql(
    """
    SELECT Year, pop_growth_pct
    FROM pop_growth_world
    ORDER BY Year DESC
    LIMIT 10;
""",
    conn,
)
print(recent)
conn.close()

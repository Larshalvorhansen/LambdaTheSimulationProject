#!/usr/bin/env python3

import wbdata
import pandas as pd
import sqlite3
import datetime
import logging
import sys
import os

# ----------------- Config ------------------
DB_PATH = "world_data.db"
TABLE_NAME = "gdp_growth"
INDICATOR_CODE = "NY.GDP.MKTP.KD.ZG"  # GDP (annual % growth)
START_YEAR = 2000
END_YEAR = datetime.datetime.now().year
# -------------------------------------------

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("gdp_fetch.log"), logging.StreamHandler(sys.stdout)],
)


def fetch_gdp_data(start_year, end_year):
    logging.info(f"Fetching GDP data from {start_year} to {end_year}")
    try:
        dates = (datetime.datetime(start_year, 1, 1), datetime.datetime(end_year, 1, 1))
        indicator = {INDICATOR_CODE: "gdp_growth"}
        df = wbdata.get_dataframe(indicator, data_date=dates, convert_date=True)
        df = df.reset_index()
        logging.info(f"Fetched {len(df)} rows of data.")
        return df

    except Exception as e:
        logging.error("Failed to fetch data", exc_info=True)
        raise


def store_to_sqlite(df, db_path, table_name):
    logging.info(f"Storing data to {db_path} (table: {table_name})")
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        logging.info("Data stored successfully.")
    except Exception as e:
        logging.error("Failed to store data", exc_info=True)
        raise


def main():
    logging.info("==== GDP Fetch Script Started ====")

    # Check internet connection
    if os.system("ping -c 1 api.worldbank.org > /dev/null 2>&1") != 0:
        logging.error("No internet connection. Exiting.")
        sys.exit(1)

    try:
        df = fetch_gdp_data(START_YEAR, END_YEAR)
        store_to_sqlite(df, DB_PATH, TABLE_NAME)
    except Exception as e:
        logging.error("Script failed.", exc_info=True)
        sys.exit(1)

    logging.info("==== Done ====")


if __name__ == "__main__":
    main()

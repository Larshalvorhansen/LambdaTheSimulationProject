import pandas as pd
import sqlite3

try:
url = "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Population%20(OWID%20based)/Population%20(OWID%20based).csv"
df = pd.read_csv(url)

conn = sqlite3.connect("owid.db")
df.to_sql("owid_population", conn, if_exists="replace", index=False)
conn.close()

except Exception as e:
    # Grab full traceback
    error_msg = traceback.format_exc()
    
    print("❌ Error occurred:\n", error_msg)
    
    # Copy to clipboard
    pyperclip.copy(error_msg)
    print("📋 Error copied to clipboard")

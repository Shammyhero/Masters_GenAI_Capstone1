import pandas as pd
import sqlite3

# Load ready Kaggle dataset
df = pd.read_csv('Updated_Car_Sales_Data.csv')

# Save it into SQLite DB
conn = sqlite3.connect('data_insights.db')
df.to_sql('car_sales', conn, if_exists='replace', index=False)
conn.close()
print("Database and table created with", len(df), "rows.") 
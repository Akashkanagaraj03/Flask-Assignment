import sqlite3

conn = sqlite3.connect("database.db")
print("Connected to database successfully")

conn.execute(
    "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT, last_name TEXT, company_name TEXT, city TEXT, state TEXT, zip TEXT, email TEXT, web TEXT, age INTEGER);"
)
print("Created table successfully!")

conn.close()

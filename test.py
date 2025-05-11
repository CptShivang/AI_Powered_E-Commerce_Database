# test.py
from app import mysql  # Import the 'mysql' object from your app.py

# Now you can use mysql.connection in this script
cur = mysql.connection.cursor()
cur.execute("SELECT 1")
result = cur.fetchone()
print(result)
cur.close()

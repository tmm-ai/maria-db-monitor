import mariadb
import sys

# Replace these values with your database connection info
config = {
    'user': 'root',
    'password': 'logistics123',
    'host': '127.0.0.1',
    'port': 3306
}

# Connect to MariaDB
try:
    conn = mariadb.connect(**config)
    cursor = conn.cursor()
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Drop the database
try:
    cursor.execute("DROP DATABASE IF EXISTS feb15_logistics")
    conn.commit()
    print("Database deleted successfully")
except mariadb.Error as e:
    print(f"Error deleting database: {e}")

# Close the connection
conn.close()

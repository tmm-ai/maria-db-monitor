import mariadb
import sys

try:
    conn = mariadb.connect(
        user="root",
        password="logistics123",
        host="127.0.0.1",
        port=3306,
        database="information_schema"
    )
    # Do something with the connection
    print("Successfully connected to MariaDB")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    sys.exit(1)
finally:
    if conn:
        conn.close()

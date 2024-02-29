import mariadb
import sys
from time import sleep

# Define your connection parameters
config = {
    'user': 'root',
    'password': 'logistics123',
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'feb15_logistics'
}

# Connect to MariaDB
try:
    conn = mariadb.connect(**config)
    cursor = conn.cursor()
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Function to force a new transaction by committing the current transaction
def force_new_transaction():
    try:
        # This commits the current transaction, if any.
        conn.commit()
    except mariadb.Error as e:
        print(f"Error committing transaction: {e}")
# Continuously check stock levels
count = 0
while count < 15:
    force_new_transaction()
    fetch_stock_sql = "SELECT warehouse_name, current_stock FROM warehouses;"
    try:
        cursor.execute(fetch_stock_sql)
        records = cursor.fetchall()  # Fetch all the results
        print("Time:", count)
        for record in records:
            name, stock = record
            if stock <= 1:
                print(f"LOW  at {name} with {stock}") 
            elif stock >= 10:
                print(f"OVER at {name} with {stock}")
    except mariadb.Error as e:
        print(f"Error fetching stock levels: {e}")
    count +=1
    print(" ")
    sleep(1.2)  

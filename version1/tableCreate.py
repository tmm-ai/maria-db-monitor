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

# Function to execute SQL
def execute_sql(sql, commit=True):
    try:
        cursor.execute(sql)
        if commit:
            conn.commit()
    except mariadb.Error as e:
        print(f"Error: {e}")

# Create new database
execute_sql("CREATE DATABASE IF NOT EXISTS feb15_logistics;", commit=False)

# Select the newly created database
execute_sql("USE feb15_logistics;", commit=False)

# SQL for creating tables
create_shipments_table = """
CREATE TABLE IF NOT EXISTS shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event VARCHAR(255),
    truck_size INT,
    origin VARCHAR(255),
    destination VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

create_warehouse_table = """
CREATE TABLE IF NOT EXISTS warehouses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_name VARCHAR(255),
    capacity INT DEFAULT 10,
    current_stock INT DEFAULT 6
);
"""

# Execute SQL
try:
    cursor.execute(create_shipments_table)
    cursor.execute(create_warehouse_table)
    # After creating the warehouses table
    warehouse_names = ["wh1", "wh2", "wh3", "cust1", "cust2", "cust3"]
    for name in warehouse_names:
        insert_warehouse_sql = f"""
        INSERT INTO warehouses (warehouse_name, capacity, current_stock) VALUES
        ('{name}', 10, 6);
        """
        execute_sql(insert_warehouse_sql)

    conn.commit()
    print("Tables created successfully")
except mariadb.Error as e:
    print(f"Error: {e}")
query_stock = """
SELECT warehouse_name, current_stock FROM warehouses;
"""
try:
    cursor.execute(query_stock)
    # Fetch all the records
    records = cursor.fetchall()
    print("Current stock in each warehouse:")
    for record in records:
        print(f"{record[0]}: {record[1]}")
except mariadb.Error as e:
    print(f"Error: {e}")
# Close the connection
conn.close()
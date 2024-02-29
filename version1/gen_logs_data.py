import mariadb
import sys
import random
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


# Function to execute SQL
def execute_sql(sql):
    try:
        cursor.execute(sql)
        conn.commit()
    except mariadb.Error as e:
        print(f"Error: {e}")


# Insert initial data
# Insert initial data
count = 0
the_warehouses = ["wh1", "wh2", "wh3", "cust1", "cust2", "cust3"]
the_truck_size = [1, 2, 3, 4]
while count < 12:
    sleep(1.2)
    count += 1
    truck_size = random.choice(the_truck_size)
    origin = random.choice(the_warehouses)
    destination = random.choice(the_warehouses)
    while origin == destination:
        destination = random.choice(the_warehouses)

    def print_warehouse_stock(warehouse_name):
        fetch_stock_sql = f"SELECT current_stock FROM warehouses WHERE warehouse_name = '{warehouse_name}';"
        try:
            cursor.execute(fetch_stock_sql)
            stock = cursor.fetchone()[0]  # Fetch the first row's first column
            # print(f"Current stock in {warehouse_name}: {stock}")
        except mariadb.Error as e:
            print(f"Error fetching stock for {warehouse_name}: {e}")

    # Before updates
    # print("Before updates: Origin, then destination")
    # print_warehouse_stock(origin)
    # print_warehouse_stock(destination)

    # Corrected to use an f-string for variable substitution
    initial_data = f"""
    INSERT INTO shipments (event, truck_size, origin, destination) VALUES
    ('shipment', {truck_size}, '{origin}', '{destination}');
    """
    execute_sql(initial_data)
    # Update origin warehouse stock
    update_sql_origin = f"""
    UPDATE warehouses
    SET current_stock = current_stock - {truck_size}
    WHERE warehouse_name = '{origin}';
    """
    execute_sql(update_sql_origin)
    # Update destination warehouse stock, corrected table name
    update_sql_destination = f"""
    UPDATE warehouses
    SET current_stock = current_stock + {truck_size}
    WHERE warehouse_name = '{destination}';
    """
    execute_sql(update_sql_destination)

    # print("AFTER updates: Origin, then destination")
    # print_warehouse_stock(origin)
    # print_warehouse_stock(destination)

    query_stock = """
    SELECT warehouse_name, current_stock FROM warehouses;
    """
    try:
        cursor.execute(query_stock)
        # Fetch all the records
        records = cursor.fetchall()
        print("Current stock at time:", count)
        for record in records:
            print(f"{record[0]}: {record[1]}")
    except mariadb.Error as e:
        print(f"Error: {e}")
    print("")

# Close the connection
conn.close()

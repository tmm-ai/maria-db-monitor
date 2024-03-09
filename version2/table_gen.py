import mariadb
import sys
import random

# Connection parameters for initial connection to drop/create database
config_init = {
    'user': 'root',
    'password': 'logistics123',
    'host': '127.0.0.1',
    'port': 3306,
}

# Connection parameters for connecting to the newly created database
config_db = {
    'user': 'root',
    'password': 'logistics123',
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'feb26_logistics'
}

# Variables for customization
number_of_warehouses = 5
trucks_per_warehouse = 4
max_truck_units = 2
warehouse_capacity = 10
warehouse_units = 7
grid_H = 4
grid_V = 3

status_descriptions = {
    1: 'idle',
    2: 'in-transit',
    3: 'flat-tire',
    4: 'crash',
    5: 'over-capacity',
    6: 'out-of-stock',
    7: 'no-truck-available'
}

def create_database():
    try:
        conn = mariadb.connect(**config_init)
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE IF EXISTS feb26_logistics")
        cursor.execute("CREATE DATABASE feb26_logistics")
        print("Database 'feb26_logistics' created successfully.")
    except mariadb.Error as e:
        print(f"Error creating database: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

def create_tables_and_populate():
    try:
        conn = mariadb.connect(**config_db)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
        CREATE TABLE status_types (
            id INT PRIMARY KEY,
            description VARCHAR(255) NOT NULL
        )""")
        cursor.execute("""
        CREATE TABLE warehouses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            capacity INT NOT NULL,
            inventory INT NOT NULL,
            vertical_loc INT,
            horizontal_loc INT
        )""")
        cursor.execute("""
        CREATE TABLE trucks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            status INT,
            vertical_loc INT,
            horizontal_loc INT,
            units INT,
            FOREIGN KEY (status) REFERENCES status_types(id)
        )""")
        cursor.execute("""
        CREATE TABLE shipments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            truck_id INT,
            amount INT,
            warehouse_from_id INT,
            warehouse_to_id INT,
            time_depart INT,
            time_driving INT,
            time_delay INT,
            time_arrived INT,
            truck_id_helping INT,
            status INT,
            completed BOOLEAN,
            FOREIGN KEY (status) REFERENCES status_types(id)
        )""")
        cursor.execute("""
        CREATE TABLE problems (
            id INT AUTO_INCREMENT PRIMARY KEY,
            truck_id INT,
            time_occured INT,
            shipment_id INT,
            warehouse_from_id INT,
            warehouse_to_id INT,
            type INT,
            time_to_fix INT,
            fixed BOOLEAN,
            FOREIGN KEY (type) REFERENCES status_types(id)
        )""")

        # Populate status_types
        for id, description in status_descriptions.items():
            cursor.execute("INSERT INTO status_types (id, description) VALUES (?, ?)", (id, description))

        # Populate warehouses and trucks
        wh_locations = set()
        horz = 1
        vert = 1
        for _ in range(number_of_warehouses):
            while (horz, vert) in wh_locations:
                horz = random.randint(1,grid_H)
                vert = random.randint(1,grid_V)
            wh_locations.add((horz, vert))
            cursor.execute("INSERT INTO warehouses (capacity, inventory, vertical_loc, horizontal_loc) VALUES (?, ?, ?, ?)", (warehouse_capacity, warehouse_units, vert, horz))
            warehouse_id = cursor.lastrowid
            for _ in range(trucks_per_warehouse):
                cursor.execute("INSERT INTO trucks (status, vertical_loc, horizontal_loc, units) VALUES (?, ?, ?, ?)",
                               (1, vert, horz, 0))  

        conn.commit()
        print("Tables created and initial data populated successfully.")
    except mariadb.Error as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_database()  # Drop and create the database
    create_tables_and_populate()  # Create tables and populate initial data

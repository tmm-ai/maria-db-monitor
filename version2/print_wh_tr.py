import mariadb
import sys

config_db = {
    'user': 'root',
    'password': 'logistics123',
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'feb26_logistics'
}

def fetch_and_print_data(conn):
    cursor = conn.cursor()
    
    # Fetch and print warehouse data
    print("\nWarehouses Data:")
    cursor.execute("SELECT id, capacity, inventory, vertical_loc, horizontal_loc FROM warehouses")
    for (id, capacity, inventory, vertical_loc, horiz_loc) in cursor:
        print(f"Warehouse ID: {id}, Capacity: {capacity}, Inventory: {inventory}, Location: ({vertical_loc}, {horiz_loc})")
    
    # Fetch and print truck data
    print("\nTrucks Data:")
    cursor.execute("SELECT t.id, t.status, s.description, t.vertical_loc, t.horizontal_loc, t.units FROM trucks t JOIN status_types s ON t.status = s.id")
    for (id, status, description, vertical_location, horizontal_loc, units) in cursor:
        print(f"Truck ID: {id}, Status: {description}, Location: ({vertical_location}, {horizontal_loc}), Units: {units}")
    
    # Fetch and print shipments data
    print("\nShipments Data:")
    cursor.execute("""
    SELECT shipments.id, shipments.amount, shipments.truck_id, shipments.warehouse_from_id, shipments.warehouse_to_id, shipments.time_depart,shipments.time_driving,shipments.time_delay, shipments.time_arrived, status_types.description AS status_description, shipments.completed
    FROM shipments
    JOIN status_types ON shipments.status = status_types.id
    """)
    shipments = cursor.fetchall()
    if shipments:
        for (id, amount, truck_id, warehouse_from_id, warehouse_to_id, time_depart, time_driving, time_delay, time_arrived, status_description, completed) in shipments:
            print(f"ID: {id},Amt: {amount} Tr_ID: {truck_id}, Fr: {warehouse_from_id}, To: {warehouse_to_id}, T_Depart: {time_depart}, Time_Dr: {time_driving},Delay: {time_delay}, Arriv: {time_arrived}, Stat: {status_description}, Compl: {completed}")
    else:
        print("No data available.")

    # Fetch and print problems data
    print("\nProblems Data:")
    cursor.execute("""
    SELECT problems.id, problems.truck_id, problems.time_occured, problems.shipment_id, problems.warehouse_from_id, problems.warehouse_to_id, status_types.description AS problem_type, problems.time_to_fix, problems.fixed
    FROM problems
    JOIN status_types ON problems.type = status_types.id
    """)
    problems = cursor.fetchall()
    if problems:
        for (id, truck_id, time_occured, shipment_id, warehouse_from_id, warehouse_to_id, problem_type, time_to_fix, fixed) in problems:
            print(f"Prob ID: {id}, Tr ID: {truck_id},Time Occur:{time_occured} Ship ID: {shipment_id}, From: {warehouse_from_id}, To: {warehouse_to_id}, Prob Type: {problem_type}, Time to Fix: {time_to_fix}, Fixed: {fixed}")
    else:
        print("No data available.")

    cursor.close()

# Modify the main function to call fetch_and_print_data after populating data
def main():

    try:
        conn = mariadb.connect(**config_db)
        fetch_and_print_data(conn)  # Fetch and print the populated data
    except mariadb.Error as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()

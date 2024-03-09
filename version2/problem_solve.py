import mariadb
import sys
import random
from time import sleep

# Connection parameters for connecting to the newly created database
config = {
    'user': 'root',
    'password': 'logistics123',
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'feb26_logistics'
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

# Function to force a new transaction by committing the current transaction
def force_new_transaction():
    try:
        # This commits the current transaction, if any.
        conn.commit()
    except mariadb.Error as e:
        print(f"Error committing transaction: {e}")
# check each new line in the problems table that was created since the last check. Check the status of each new line.
# If status is 5: 'over-capacity', then
# subtract 2 from the inventory of the warehouse_from_id and add 2 to the extra_inventory variable. 
# If the status is 6: 'out-of-stock', then
# subtract 2 from the extra_inventory variable and add 2 to the inventory of the warehouse_to_id. 
# If the status is 7: 'no-truck-available', then 
# subtract 1 from the extra_trucks variable and add 1 new truck to the trucks table at the location of the warehouse_from_id.
def check_problems(extra_inventory, extra_trucks, the_time):
    force_new_transaction()
    cursor.execute("""
    SELECT problems.id, problems.truck_id, problems.time_occured, problems.shipment_id, problems.warehouse_from_id, problems.warehouse_to_id, status_types.description AS problem_type, problems.time_to_fix, problems.fixed
    FROM problems
    JOIN status_types ON problems.type = status_types.id
    """)
    problems = cursor.fetchall()
    
    if problems:
        for (id, truck_id, time_occured, shipment_id, warehouse_from_id, warehouse_to_id, type, time_to_fix, fixed) in problems:
            if not fixed and type != "flat-tire":
                print("problem type:", type, fixed)
                if type == 'over-capacity':
                    if extra_inventory > 2:
                        print("TOO MUCH extra inventory to fix this problem. NOTIFY MGMT")
                    else:
                        execute_sql(f"UPDATE warehouses SET inventory = inventory - 2 WHERE id = {warehouse_from_id}")
                        extra_inventory += 2
                        execute_sql(f"UPDATE problems SET fixed = 1 WHERE id = {id}")
                elif type == 'out-of-stock':
                    if extra_inventory < 2:
                        print("Not enough extra inventory to fix this problem. NOTIFY MGMT")
                    else:
                        extra_inventory -= 2
                        execute_sql(f"UPDATE warehouses SET inventory = inventory + 2 WHERE id = {warehouse_to_id}")
                        execute_sql(f"UPDATE problems SET fixed = 1 WHERE id = {id}")
                elif type == 'no-truck-available':
                    if extra_trucks < 1:
                        print("Not enough extra trucks to fix this problem. NOTIFY MGMT")
                    else:
                        extra_trucks -= 1
                        execute_sql(f"INSERT INTO trucks (status, vertical_loc, horizontal_loc, units) VALUES (1, (SELECT vertical_loc FROM warehouses WHERE id = {warehouse_from_id}), (SELECT horizontal_loc FROM warehouses WHERE id = {warehouse_from_id}), 2)")
                        execute_sql(f"UPDATE problems SET fixed = 1 WHERE id = {id}")
                elif type == "flat-tire":
                    if time_occured + time_to_fix <= the_time:
                        execute_sql(f"UPDATE problems SET fixed = 1 WHERE id = {id}")
                        # update shipment status to in-transit
                        execute_sql(f"UPDATE shipments SET status = 2 WHERE id = {shipment_id}")
    else:
        print("No new problems to check.")


if __name__ == "__main__":
    the_time = 0
    extra_inventory = 6
    extra_trucks = 6    
    while the_time < 16:
        check_problems(extra_inventory, extra_trucks, the_time)
        sleep(.3)
        the_time +=1
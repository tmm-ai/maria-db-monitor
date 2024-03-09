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

def fetch_warehouse_locations(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT vertical_loc, horizontal_loc FROM warehouses")
    locations = cursor.fetchall()
    cursor.execute("SELECT id FROM warehouses")
    ids = cursor.fetchall()
    cursor.close()
    # Convert the fetched data into a list of tuples
    location_list = [(vertical_loc, horizontal_loc) for vertical_loc, horizontal_loc in locations]
    ids_list = [id[0] for id in ids]
    return location_list, ids_list

def fetch_trucks_at_specific_warehouse(conn, warehouse_id):
    cursor = conn.cursor()
    query = """
    SELECT t.id
    FROM trucks t
    WHERE t.status = 1 AND t.vertical_loc = (SELECT vertical_loc FROM warehouses WHERE id = ?) AND t.horizontal_loc = (SELECT horizontal_loc FROM warehouses WHERE id = ?)
    """
    cursor.execute(query, (warehouse_id, warehouse_id))
    truck_ids_at_warehouse = cursor.fetchall()
    cursor.close()
    # Convert the fetched data into a list of truck IDs
    truck_ids_list = [truck_id for (truck_id,) in truck_ids_at_warehouse]
    return truck_ids_list



def process_new_deliveries(the_time, shipment):
    print("depart:", shipment[4], "drive:", shipment[5], "delay:", shipment[6])
    # HAS shipment arrived at destination?
    if the_time >= shipment[4] + shipment[5] + shipment[6]:
        # check if warehouse is over capacity
        cursor.execute("SELECT capacity, inventory FROM warehouses WHERE id = ?", (shipment[3],))   
        warehouse = cursor.fetchall()
        if warehouse[0][1] + shipment[1] > warehouse[0][0]:
            cursor.execute("INSERT INTO problems (time_occured, warehouse_from_id, warehouse_to_id, type, time_to_fix, fixed) VALUES (?,?,?,?,?,?)", (the_time, shipment[2], shipment[3], 5, 0, False))
            print("OVER CAPACITY: Warehouse:", shipment[3])
        else:
            cursor.execute("UPDATE shipments SET status = 1, completed = True, time_arrived = ? WHERE truck_id = ? AND warehouse_to_id = ? AND time_depart + time_driving + time_delay <= ?", (the_time, shipment[0], shipment[3], the_time))
            cursor.execute("UPDATE warehouses SET inventory = inventory + ? WHERE id = ?", (shipment[1], shipment[3]))
            # set truck status to 1, and its vertical and horizontal location to the warehouse_to_id and set units to 0.
            cursor.execute("UPDATE trucks SET status = 1, vertical_loc = (SELECT vertical_loc FROM warehouses WHERE id = ?), horizontal_loc = (SELECT horizontal_loc FROM warehouses WHERE id = ?), units = 0 WHERE id = ?", (shipment[3], shipment[3], shipment[0]))
        conn.commit()

def update_truck_locations(the_time, shipment):
    # getting trucks that have not compelted shipment
    cursor.execute("SELECT vertical_loc, horizontal_loc FROM trucks WHERE id = ?", (shipment[0],))
    truck_location = cursor.fetchall()
    # get warehouse_to_id location
    cursor.execute("SELECT vertical_loc, horizontal_loc FROM warehouses WHERE id = ?", (shipment[3],))
    warehouse_location = cursor.fetchall()
    # UPDATING TRUCK LOCATIONS WHILE IN TRANSIT
    # if the truck's vertical_loc is not the same as the warehouse_to_id, the change the truck's vertical_loc
    # to make it one unit closer to the warehouse_to_id. If they are the same, then change the truck's horizontal_loc by 1 unit closer to that of the warehouse_to_id.
    
    if truck_location[0][0] != warehouse_location[0][0]:
        if truck_location[0][0] < warehouse_location[0][0]:
            cursor.execute("UPDATE trucks SET vertical_loc = ? WHERE id = ?", (truck_location[0][0] + 1, shipment[3]))
        else:
            cursor.execute("UPDATE trucks SET vertical_loc = ? WHERE id = ?", (truck_location[0][0] - 1, shipment[3]))
    else:
        if truck_location[0][1] < warehouse_location[0][1]:
            cursor.execute("UPDATE trucks SET horizontal_loc = ? WHERE id = ?", (truck_location[0][1] + 1, shipment[3]))
        else:
            cursor.execute("UPDATE trucks SET horizontal_loc = ? WHERE id = ?", (truck_location[0][1] - 1, shipment[3]))
    conn.commit()
    # FLAT TIRE: if shipment is not completed, and status is in transit, and random number is less than 5, then update status to 3 (FLAT TIRE), and time_delay to 2
    # if the status of the shipment is in transit, and the random number is less than 5, then update the status to 3 (flat tire) and time_delay to 2+time_delay
    if random.randint(1, 100) <= 5:
        cursor.execute("UPDATE shipments SET status = 3, time_delay = ? WHERE truck_id = ? AND warehouse_to_id = ?", (shipment[6]+2,shipment[0], shipment[3]))
        print("DELAYED: Truck w/Flat Tire:",shipment[0],"To warehouse:", shipment[3]) 
        # update problems table
        cursor.execute("INSERT INTO problems (truck_id, time_occured, shipment_id, warehouse_from_id, warehouse_to_id, type, time_to_fix, fixed) VALUES (?,?,?,?,?,?,?,?)", (shipment[0],the_time, shipment[10], shipment[2], shipment[3], 3, 2, False))
        conn.commit()
    
def process_ongoing_deliveries(the_time):
    # Gathering current shipment data
    cursor = conn.cursor()
    cursor.execute("SELECT truck_id, amount, warehouse_from_id, warehouse_to_id, time_depart, time_driving, time_delay, time_arrived, status, completed, id FROM shipments WHERE completed = False")
    
    the_shipments = cursor.fetchall()
    # Updating Shipments that have just arrived at destination. if it has, update status to 1, completed to True. Then add tr_size to warehouse_to_id inventory
    print("Current Time:", the_time)
    for shipment in the_shipments:
        # if the shipment is not completed:
        if shipment[9] == False:
            process_new_deliveries(the_time, shipment)
            update_truck_locations(the_time, shipment)

    cursor.close()
    

def create_new_shipments(the_time):

    # for each warehouse, if inventory < 10, create a shipment to a random warehouse
    cursor = conn.cursor()
    cursor.execute("SELECT id, inventory FROM warehouses")
    the_warehouses = cursor.fetchall()
    truck_size = [1, 2]
    for warehouse in the_warehouses:
        warehouse_locations, warehouse_ids = fetch_warehouse_locations(conn)
        # choosing amount, origin, destination of shipment
        tr_size = random.choice(truck_size)
        origin = warehouse[0]
        destination = random.choice(warehouse_ids)
        while origin == destination:
            destination = random.choice(warehouse_ids)
        # IS Inventory Available?  if not, add to problems table
        if warehouse[1] < tr_size:
            # Create line in problem table stating that there is not enough inventory to ship
            cursor.execute("INSERT INTO problems (time_occured, warehouse_from_id, warehouse_to_id, type, time_to_fix, fixed) VALUES (?,?,?,?,?,?)", (the_time, origin, destination, 6, 0, False))
            print("Not enough inventory to ship from:", origin)
            conn.commit()
            continue
        trucks_available = fetch_trucks_at_specific_warehouse(conn, origin)
        # IS truck available at origin?  if not, add to problems table
        if len(trucks_available) == 0:
            cursor.execute("INSERT INTO problems (time_occured, warehouse_from_id, warehouse_to_id, type, time_to_fix, fixed) VALUES (?,?,?,?,?,?)", (the_time, origin, destination, 7, 0, False))
            conn.commit()
            print("No trucks available at warehouse", origin, "to deliver to warehouse", destination, "at time", the_time)
            continue
        
        # determining total distance in units of driving time
        total_distance = abs(warehouse_locations[origin-1][0] - warehouse_locations[destination-1][0])+ \
            abs(warehouse_locations[origin-1][1] - warehouse_locations[destination-1][1])
        # Printing shipping information
        print("trucks",trucks_available[0],trucks_available )       
        print("origin",origin,"destination",destination,"Amount", tr_size,"Total Distance:", total_distance)
        print("---")
        cursor = conn.cursor()

        # We have a shipment ready to go now
        # Insert shipment into shipment page
        cursor.execute("INSERT INTO shipments (truck_id, amount, warehouse_from_id, warehouse_to_id, time_depart, time_driving, time_delay, status, completed)\
                        VALUES (?,?,?,?,?,?,?,?,?)", ( trucks_available[0], tr_size, origin, destination, the_time,total_distance,0,2, False))
        # Update truck status to 2(in transit), update units/truck size
        cursor.execute("UPDATE trucks SET status = 2, units = ? WHERE id = ?", (tr_size, trucks_available[0]))
        # Remove units from warehouse inventory
        cursor.execute("UPDATE warehouses SET inventory = inventory - ? WHERE id = ?", (tr_size, origin))
        # Remove truck from trucks_available
        trucks_available.pop(0)

        conn.commit() 
    cursor.close()

def gen_data():
    the_time = 0
    while the_time < 10:
        the_time +=1
        process_ongoing_deliveries(the_time)
        create_new_shipments(the_time)
        sleep(.2)

        
 
    # try:
    #     cursor.execute(query_stock)
    #     # Fetch all the records
    #     records = cursor.fetchall()
    #     print("Current stock at time:", count)
    #     for record in records:
    #         print(f"{record[0]}: {record[1]}")
    # except mariadb.Error as e:
    #     print(f"Error: {e}")
    # print("")

# Close the connection
    conn.close()



if __name__ == "__main__":
    gen_data()  # Drop and create the database


# TODO: flat tire now increments delay time by 2
    # flat tire status is updated to in-transit once fixed. 
    # added arrival times to shipments
# shipment status is not right. flat tire with complete, 
# get rid of delay of 4 from ???
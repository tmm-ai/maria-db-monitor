""" 
three phases
1 - just make random deliveries, update wh volumes, and new truck dest, print after 20
1.5 - track truck locations, print after 20
2 - warehouses get too full or empty, have trucks wait up to 4 periods. Add problems
3 - trucks get flat tires wait 2 periods. add problems - 10%
4 - trucks crash and need to get help.  wait 5 periods + new truck. add problems 10%

# pick 1) warehouse in, out and units at random
# select 1st idle truck at warehouse from truck list
# add entry to shipment list. 
"""

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
    JOIN warehouses w ON t.vertical_loc = w.vertical_loc AND t.horizontal_loc = w.horizontal_loc
    WHERE w.id = %s
    """
    cursor.execute(query, (warehouse_id,))
    truck_ids_at_warehouse = cursor.fetchall()
    cursor.close()
    # Convert the fetched data into a list of truck IDs
    truck_ids_list = [truck_id for (truck_id,) in truck_ids_at_warehouse]
    return truck_ids_list

def process_ongoing_deliveries(the_time):
    # if status is in transit: if current time == time_depart+time driving - COMPLETE, 
    # then time_arrived = current time, status = idle.
    cursor = conn.cursor()
    cursor.execute("SELECT truck_id, amount, warehouse_to_id, time_depart, time_driving, time_delay, time_arrived, status, completed FROM shipments WHERE completed = False")
    
    the_shipments = cursor.fetchall()
    # go one by one, check if shipment has arrived via time, if it has, update status to 1, completed to True. Then add tr_size to warehouse_to_id inventory
    print("Current Time:", the_time)
    for shipment in the_shipments:
        print("depart:", shipment[3], "drive:", shipment[4], "delay:", shipment[5])
        if the_time >= shipment[3] + shipment[4] + shipment[5]:
            cursor.execute("UPDATE shipments SET status = 1, completed = True WHERE truck_id = ? AND warehouse_to_id = ? AND time_depart + time_driving + time_delay <= ?", (shipment[0], shipment[2], the_time))
            cursor.execute("UPDATE warehouses SET inventory = inventory + ? WHERE id = ?", (shipment[1], shipment[2]))
            # set truck status to 1, and its vertical and horizontal location to the warehouse_to_id and set units to 0.
            cursor.execute("UPDATE trucks SET status = 1, vertical_loc = (SELECT vertical_loc FROM warehouses WHERE id = ?), horizontal_loc = (SELECT horizontal_loc FROM warehouses WHERE id = ?), units = 0 WHERE id = ?", (shipment[2], shipment[2], shipment[0]))
            
    conn.commit()
    
    # for shipments that are not completed, with a 5% chance, randomly add a time_delay of 2 and update status to 3 to each uncommented shipment. 
    # Rewrite and fix: cursor.execute("SELECT truck_id, amount, warehouse_to_id, time_depart, time_driving, time_delay, status, completed FROM warehouses WHERE completed =False, status = 2")
    cursor.execute("SELECT id, truck_id, amount, warehouse_to_id, time_depart, time_driving, time_delay, status, completed FROM shipments WHERE completed =False")
    the_shipments = cursor.fetchall()
    for shipment in the_shipments:
        # if the truck's vertical_loc is not the same as the warehouse_to_id, the change the truck's vertical_loc
        # to make it one unit closer to the warehouse_to_id. If they are the same, then change the truck's horizontal_loc by 1 unit closer to that of the warehouse_to_id.
        if shipment[7] == 2:
            cursor.execute("SELECT vertical_loc, horizontal_loc FROM trucks WHERE id = ?", (shipment[1],))
            truck_location = cursor.fetchall()
            #get warehouse_to_id location
            cursor.execute("SELECT vertical_loc, horizontal_loc FROM warehouses WHERE id = ?", (shipment[3],))
            warehouse_location = cursor.fetchall()
            print("truck_location",truck_location)
            print("warehouse_location",warehouse_location)
        # if the truck's vertical_loc is not the same as the warehouse_to_id, the change the truck's vertical_loc
        # to make it one unit closer to the warehouse_to_id. If they are the same, then change the truck's horizontal_loc by 1 unit closer to that of the warehouse_to_id.
            if truck_location[0][0] != warehouse_location[0][0]:
                if truck_location[0][0] < warehouse_location[0][0]:
                    cursor.execute("UPDATE trucks SET vertical_loc = ? WHERE id = ?", (truck_location[0][0] + 1, shipment[1]))
                else:
                    cursor.execute("UPDATE trucks SET vertical_loc = ? WHERE id = ?", (truck_location[0][0] - 1, shipment[1]))
            else:
                if truck_location[0][1] < warehouse_location[0][1]:
                    cursor.execute("UPDATE trucks SET horizontal_loc = ? WHERE id = ?", (truck_location[0][1] + 1, shipment[1]))
                else:
                    cursor.execute("UPDATE trucks SET horizontal_loc = ? WHERE id = ?", (truck_location[0][1] - 1, shipment[1]))
            conn.commit()


        # if shipment is not completed, and status is in transit, and random number is less than 5, then update status to 3 (FLAT TIRE), and time_delay to 2
        if random.randint(1, 100) <= 5:
            cursor.execute("UPDATE shipments SET status = 3, time_delay = 2 WHERE truck_id = ? AND warehouse_to_id = ?", (shipment[1], shipment[3]))
            print("DELAYED: Truck:",shipment[1],"To warehouse:", shipment[3])
            # update problems table
            cursor.execute("INSERT INTO problems (truck_id, shipment_id, warehouse_from_id, warehouse_to_id, type, time_to_fix) VALUES (?,?,?,?,?,?)", (shipment[1], shipment[0], shipment[3], shipment[4], 3, 2))
            conn.commit()
    cursor.close()
    

def create_new_shipments(the_time):

    # for each warehouse, if inventory < 10, create a shipment to a random warehouse
    cursor = conn.cursor()
    cursor.execute("SELECT id, inventory FROM warehouses")
    the_warehouses = cursor.fetchall()
    truck_size = [1, 2]
    for warehouse in the_warehouses:
        if warehouse[1] > 0:
            warehouse_locations, warehouse_ids = fetch_warehouse_locations(conn)
            # choosing amount, origin, destination of shipment
            tr_size = random.choice(truck_size)
            origin = warehouse[0]
            destination = random.choice(warehouse_ids)
            while origin == destination:
                destination = random.choice(warehouse_ids)
            
            trucks_available = fetch_trucks_at_specific_warehouse(conn, origin)
            # determine if truck available at origin, and if not, add to problems table
            if len(trucks_available) == 0:
                cursor.execute("INSERT INTO problems (warehouse_from_id, warehouse_to_id, type, time_to_fix) VALUES (?,?,?,?)", (origin, destination, 7, 4))
                conn.commit()
                print("No trucks available at warehouse", origin, "to deliver to warehouse", destination, "at time", the_time)
                continue
            print("trucks",trucks_available[0],trucks_available )
            # determining total distance / time driving
            print("origin",origin)
            print("destination",destination)
            print("from",warehouse_locations[origin-1], "TO",warehouse_locations[destination-1] )
            total_distance = abs(warehouse_locations[origin-1][0] - warehouse_locations[destination-1][0])+ \
                abs(warehouse_locations[origin-1][1] - warehouse_locations[destination-1][1])
            print("Amount", tr_size)
            print("Total Distance:", total_distance)
            print("---")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO shipments (truck_id, amount, warehouse_from_id, warehouse_to_id, time_depart, time_driving, time_delay, status, completed)\
                            VALUES (?,?,?,?,?,?,?,?,?)", ( trucks_available[0], tr_size, origin, destination, the_time,total_distance,0,2, False))
            # TODO: update truck status to 2, update units/truck size
            cursor.execute("UPDATE trucks SET status = 2, units = ? WHERE id = ?", (tr_size, trucks_available[0]))
            # remove units from warehouse inventory
            cursor.execute("UPDATE warehouses SET inventory = inventory - ? WHERE id = ?", (tr_size, origin))
            # remove truck from trucks_available
            trucks_available.pop(0)
            conn.commit() 
    cursor.close()

def gen_data():
    the_time = 0
    while the_time < 8:
        the_time +=1
        process_ongoing_deliveries(the_time)
        create_new_shipments(the_time)
        sleep(0.2)

        
    
    # cursor.execute("""
    # SELECT shipments.id, shipments.truck_id, shipments.warehouse_from_id, shipments.warehouse_to_id, shipments.time_depart,shipments.time_driving,shipments.time_delay, shipments.time_arrived, status_types.description AS status_description, shipments.completed
    # FROM shipments
    # JOIN status_types ON shipments.status = status_types.id
    # """)


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


# TODO: what to do once no truck is available? Add to processing to wait. 
# TOTO: what to do once inventory is empty?  Add to processing to wait??
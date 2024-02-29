# Module Import
import mariadb
import sys

# Print List of Contacts
def print_contacts(cur):
     """Retrieves the list of contacts from the database and prints to stdout"""

     # Initialize Variables
     contacts = []

     # Retrieve Contacts
     cur.execute("SELECT first_name, last_name, email FROM test.contacts")

     # Prepare Contacts
     for (first_name, last_name, email) in cur:
        contacts.append(f"{first_name} {last_name} <{email}>")

     # List Contacts
     print("\n".join(contacts))

# Instantiate Connection
try:
     conn = mariadb.connect(
        host="192.0.2.1",
        port=3306,
        user="db_user",
        password="logistics123")

     # Instantiate Cursor
     cur = conn.cursor()

     print_contacts(cur)

     # Close Connection
     conn.close()

except mariadb.Error as e:
      print(f"Error connecting to the database: {e}")
      sys.exit(1)

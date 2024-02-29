import mariadb
import sys

# Connection configuration
config = {
    'user': 'root',
    'password': 'logistics123',
    'host': '127.0.0.1',
    'port': 3306,
}

# Connect to MariaDB
try:
    conn = mariadb.connect(**config)
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    sys.exit(1)

# Cursor to execute queries
cursor = conn.cursor()

# Detailed queries for each database
queries = {
    'information_schema': [
        ('CHARACTER_SETS', 'SELECT CHARACTER_SET_NAME, DEFAULT_COLLATE_NAME, DESCRIPTION FROM CHARACTER_SETS;'),
        ('COLLATIONS', 'SELECT COLLATION_NAME, CHARACTER_SET_NAME, ID, IS_DEFAULT FROM COLLATIONS;'),
        ('TABLES', 'SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE FROM TABLES WHERE TABLE_SCHEMA NOT IN ("information_schema", "mysql", "performance_schema") LIMIT 5;')
    ],
    'mysql': [
        ('user', 'SELECT User, Host, authentication_string FROM user;'),
        ('db', 'SELECT Db, Host, User, Select_priv, Insert_priv FROM db;')
    ],
    'performance_schema': [
        ('events_statements_summary_by_digest', 'SELECT SCHEMA_NAME, DIGEST, DIGEST_TEXT, COUNT_STAR, SUM_TIMER_WAIT FROM events_statements_summary_by_digest ORDER BY SUM_TIMER_WAIT DESC LIMIT 5;'),
        ('file_summary_by_event_name', 'SELECT EVENT_NAME, COUNT_READ, SUM_NUMBER_OF_BYTES_READ FROM file_summary_by_event_name ORDER BY SUM_NUMBER_OF_BYTES_READ DESC LIMIT 5;')
    ]
}

for db, db_queries in queries.items():
    try:
        print(f"\nExploring database: {db}")
        cursor.execute(f"USE {db};")
        for table_name, query in db_queries:
            print(f"\nTable: {table_name}")
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            print(", ".join(columns))
            for row in cursor:
                print(row)
    except mariadb.Error as e:
        print(f"Error accessing {db}: {e}")

# Close the connection
conn.close()

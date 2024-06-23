import sqlite3

def get_all_table_data(db_name, table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Execute a SQL query to get all data from the specified table
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)

    # Fetch all rows from the executed query
    rows = cursor.fetchall()

    # Get column names from the table
    column_names = [description[0] for description in cursor.description]

    # Close the connection
    conn.close()

    return column_names, rows

# Usage example
db_name = 'database.db'
table_name = 'users'

column_names, rows = get_all_table_data(db_name, table_name)

# Print column names
print("Column names:", column_names)

# Print each row of data
for row in rows:
    print(row)

import mysql.connector

# Replace these with your database connection details
host = '127.0.0.1'
user = 'root'
password = 'Betula123'
database = 'betula'

# Establish a connection to the database
connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# Create a cursor
cursor = connection.cursor()

# Example: SELECT query
query = "SELECT * FROM user_information"
cursor.execute(query)

# Fetch and print the results
for row in cursor.fetchall():
    print(row)

# Close the cursor and connection
cursor.close()
connection.close()
'''
References Below
Videos:
https://www.youtube.com/watch?v=6joGkZMVX4o 
https://www.youtube.com/watch?v=JVtGKA6OVvM 

Documents:
https://www.mssqltips.com/sqlservertip/4037/storing-passwords-in-a-secure-way-in-a-sql-server-database/
'''

from pypyodbc_main import pypyodbc as odbc # Run if on Mac Apple Silicon
#import pypyodbc as odbc # Run if on Windows
import pandas as pd
from credential import username, password

#server = "betula-server.database.windows.net"
#db = "BetulaDB"
connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
connection = odbc.connect(connection_string)
create_user_table_query = '''
        CREATE TABLE USER_DATA(
        UserID INT IDENTITY NOT NULL PRIMARY KEY,
        FirstName VARCHAR(255),
        LastName VARCHAR(255),
        Email VARCHAR(255),
        Username VARCHAR(255),
        Password BINARY(64)
        )
    '''

create_cursor = connection.cursor()
try:
    create_cursor.execute(create_user_table_query)
    print("User Table created successfully")
except:
    print("User Table not created")


get_user_table_data_query = "SELECT * FROM USER_DATA"
select_cursor = connection.cursor()
select_cursor.execute(get_user_table_data_query)
dataset = select_cursor.fetchall()

# Get Column Names
headers = [column[0] for column in select_cursor.description]

df = pd.DataFrame(columns=headers, data=dataset)
print(df)



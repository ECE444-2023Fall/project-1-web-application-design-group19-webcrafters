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
from credentials import db_username, db_password

#server = "betula-server.database.windows.net"
#db = "BetulaDB"
connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
connection = odbc.connect(connection_string)

# query = '''
#             CREATE TABLE EVENT_DATA(
#                 Event_ID INT IDENTITY NOT NULL PRIMARY KEY,
#                 Event_Name VARCHAR(255),
#                 Coordinator_Name VARCHAR(255),
#                 Coordinator_Email VARCHAR(255),
#                 Coordinator_Username VARCHAR(255),
#                 Organization_Name VARCHAR(255),
#                 Target_Campus VARCHAR(255),
#                 Event_Description TEXT,
#                 Event_Month VARCHAR(255),
#                 Event_Date INT,
#                 Event_Year INT,
#                 Event_Start_Time TIME,
#                 Event_End_Time TIME,
#                 Event_Street_Address VARCHAR(255),
#                 Event_City VARCHAR(255),
#                 Event_Postal_Code VARCHAR(255),
#                 Event_Location_Common_Name VARCHAR(255),
#                 Target_College VARCHAR(255),
#                 Target_Faculty VARCHAR(255),
#                 Event_Cost DECIMAL,
#                 Tags VARCHAR(255)
#             )
# '''

# query = '''
#     DROP TABLE USER_DATA
# '''

query = '''
        CREATE TABLE USER_DATA(
        User_ID INT IDENTITY NOT NULL PRIMARY KEY,
        User_First_Name VARCHAR(255),
        User_Last_Name VARCHAR(255),
        User_Email VARCHAR(255),
        Username VARCHAR(255),
        Password VARCHAR(255),
        Account_Type VARCHAR(255),
        User_Tags VARCHAR(255),
        Recs_Must_Match BIT
        )
    '''

check_table_exists_query = '''
        IF EXISTS (SELECT * 
                    FROM DBO.USER_DATA)
    '''

create_cursor = connection.cursor()
check_cursor = connection.cursor()

try:
    '''
    if (check_cursor.execute(check_table_exists_query)):
        print("Table already exists")
        pass
    '''
    create_cursor.execute(query)
    create_cursor.commit()
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


create_cursor.close()
check_cursor.close()
select_cursor.close()
connection.close()

print("Cursors and DB Closed")





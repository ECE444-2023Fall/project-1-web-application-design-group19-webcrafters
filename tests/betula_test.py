import pytest

from betula import app
from pypyodbc_main import pypyodbc as odbc
import pandas as pd
from credentials import db_username, db_password

import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def login(client, email, password):
    return client.post(
        "/login",
        data=dict(email=email, password=password),
        follow_redirects=True
    )

def join(client, email, username, password, accountType):
    return client.post(
        "/join",
        data=dict(email=email, username=username, password=password, rePassword=password, accountType=accountType),
        follow_redirects=True
    )

def get_user_data(email, username, password, accountType):
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    connection = odbc.connect(connection_string)

    check_user_exists_query = f'''
                        SELECT COUNT(*) 
                        FROM USER_DATA
                        WHERE User_Email = '{email}' AND Username = '{username}' AND Password = '{password}' AND Account_Type = '{accountType}'
                    '''

    cursor = connection.cursor()
    cursor.execute(check_user_exists_query)
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result


# Gordon
# Test login capability of the system
def test_login(client):
    res = login(client, "admin@admin.com", "admin")
    assert b"You were logged in" in res.data
    res = login(client, "nonsense", "admin")
    assert b"Invalid username" in res.data
    res = login(client, "admin@admin.com", "nonsense")
    assert b"Invalid password" in res.data

# Gordon
# Test join/signup capability of the system
def test_join(client):
    res = join(client, "email@email.com", "reg", "admin", "regular")
    assert b"Successfully joined" in res.data
    res = join(client, "email@email.com", "club", "admin", "club")
    assert b"Successfully joined" in res.data

# Tyler
# Test 
def test_club_user_post(client):
    """ Make sure only users with a club account can post events """
    # Check that regular account doesn't add any data when trying to post
    res = join(client, "email@email.com", "reg", "admin", "regular")
    rv = client.post(
        "/posting",
        data={      
                'organization': 'organization',
                'campus': 'campus',
                'event': 'event',
                'description': 'description',
                'date': 'date',
                'startTime': '1',
                'endTime': '2',
                'street': 'street',
                'city': 'city',
                'postal': 'postal',
                'commonName': 'commonName',
                'college': 'college',
                'faculty': 'faculty',
                'cost': '20',
                'tags': 'tags'
            }
    )
    assert b"No events here so far" in rv.data
    assert b"organization" not in rv.data
    assert b"event" not in rv.data
    assert b"description" not in rv.data

    # Check that club account adds data when trying to post
    res = join(client, "email@email.com", "reg", "admin", "club")
    rv = client.post(
        "/posting",
        data={      
                'organization': 'organization',
                'campus': 'campus',
                'event': 'event',
                'description': 'description',
                'date': 'date',
                'startTime': '1',
                'endTime': '2',
                'street': 'street',
                'city': 'city',
                'postal': 'postal',
                'commonName': 'commonName',
                'college': 'college',
                'faculty': 'faculty',
                'cost': '20',
                'tags': 'tags'
            }
    )
    assert b"No events here so far" not in rv.data
    assert b"organization" in rv.data
    assert b"event" in rv.data
    assert b"description" in rv.data
    

# Jessica
# Test the rendering of posting page
def test_posting_page_rendering(client):
    res = client.get('/posting')
    assert res.status_code == 200

# Jessica
# Test posting interface with complete input
def test_posting_complete_submission(client):
    data = {
        'organization': 'TestOrg',
        'campus': 'TestCampus',
        'event': 'TestEvent',
        'description': 'TestDescription',
        'date': 'TestDate',
        'startTime': 'TestStartTime',
        'endTime': 'TestEndTime',
        'street': 'TestStreet',
        'city': 'TestCity',
        'postal': 'TestPostal',
        'commonName': 'TestCommonName',
        'college': 'TestCollege',
        'faculty': 'TestFaculty',
        'cost': 'TestCost',
        'tags': 'TestTags'
    }
    res = client.post('/posting', data=data)
    assert res.status_code == 200

# Jessica
# Test posting interface with only required input
def test_posting_required_submission(client):
    data = {
        'organization': 'TestOrg',
        'campus': 'TestCampus',
        'event': 'TestEvent',
        'description': 'TestDescription',
        'date': 'TestDate',
        'startTime': 'TestStartTime',
        'endTime': 'TestEndTime',
        'college': 'TestCollege',
        'cost': 'TestCost'
    }
    res = client.post('/posting', data=data)
    assert res.status_code == 200


# Aniqa    
# Test if user can be added to User_Table in database
def testing_adding_new_user_to_database(client):
    
    user_data = {
        "email" : "test@betula.ca",
        "username" : "test",
        "password" : "test",
        "accountType" : "club",
    }

    user_data_json = json.dumps(user_data)

    res = client.post('/join', data=user_data_json)
    assert res.status_code == 200

    res = get_user_data(email= user_data["email"], username=user_data["username"], password=user_data["password"], accountType=user_data["accountType"])[0]
    assert res == 1


#Sean
#Testing event database access
def test_event_access(client):
    # Link form to User_Data Table in DB
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    
    couldAccess = False

    #Try to connect to database
    try:
        connection = odbc.connect(connection_string)
        couldAccess = True
    except:
        #If we could not, we should get an error
        couldAccess = False
        assert couldAccess != False

    #If we could connect to database
    if (couldAccess):
        select_user_cursor = connection.cursor()
        
        #Now that we have the user information, let's grab the events
        eventsList = []
        get_user_table_data_query = f"SELECT * FROM EVENT_DATA"
        select_user_cursor.execute(get_user_table_data_query)
        dataset = select_user_cursor.fetchall()

        # Get Column Names and match dataframe
        headers = [column[0] for column in select_user_cursor.description]
        events_df = pd.DataFrame(columns=headers, data=dataset)
        
        #Count the number of events
        numEvents = 0

        #Iterate through events and add matches matches
        for index, row in events_df.iterrows():
            numEvents += 1

        select_user_cursor.close()
        connection.close()

        #Assuming we successfully got the events from the database, there should be a non-zero number of events
        assert numEvents != 0

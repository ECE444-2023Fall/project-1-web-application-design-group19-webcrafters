import unittest
import sys
import os

# Needed to run on my computer, adjust as needed
sys.path.append(r'C:\Users\avamj\project-1-web-application-design-group19-webcrafters') 

from credentials import db_username, db_password
from betula import app  # Import your Flask app
from pypyodbc_main import pypyodbc as odbc

# This is Ava's Test Case
class TestPostingFunction(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    def test_posting_function(self):
        with self.app as client:
            data = {
                'organization': 'TestOrg',
                'campus': 'TestCampus',
                'event': 'TestEvent',
                'description': 'TestDescription',
                'date': '2023-10-29',
                'startTime': '10:00',
                'endTime': '12:00',
                'street': 'TestStreet',
                'city': 'TestCity',
                'postal': '12345',
                'commonName': 'TestCommonName',
                'college': 'TestCollege',
                'faculty': 'TestFaculty',
                'cost': 'Free',
                'tags': 'TestTag1, TestTag2'
            }

            response = client.post('/posting', data=data)
            self.assertEqual(response.status_code, 200)

            connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
            connection = odbc.connect(connection_string)
            cursor = connection.cursor()

            # Query the database to check if the event has been added
            event_query = f"SELECT * FROM EVENT_DATA WHERE Event_name = 'TestEvent' AND Organization_Name = 'TestOrg'"
            cursor.execute(event_query)
            event = cursor.fetchone()

            # Assertions to check if the event has been added to the database
            self.assertIsNotNone(event, "Event was not found in the database")  # Check if the event exists in the database

            # Check the specific details of the event in the database
            if event:
                self.assertEqual(event.Event_name, 'TestEvent')
                self.assertEqual(event.Organization_Name, 'TestOrg')

            cursor.close()
            connection.close()

if __name__ == '__main__':
    unittest.main()
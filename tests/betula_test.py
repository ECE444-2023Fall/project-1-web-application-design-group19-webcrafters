import pytest

from betula import app

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
        data=dict(organization = "organization",
                    campus = "campus",
                    event = "event",
                    description = "description",
                    date = "date",
                    startTime = 1,
                    endTime = 2,
                    street = "street",
                    city = "city",
                    postal = "postal",
                    commonName = "commonName",
                    college = "college",
                    faculty = "faculty",
                    cost = 20,
                    tags = "tags"),
        follow_redirects=True,
    )
    assert b"No events here so far" in rv.data
    assert b"organization" not in rv.data
    assert b"event" not in rv.data
    assert b"description" not in rv.data

    # Check that club account adds data when trying to post
    res = join(client, "email@email.com", "reg", "admin", "club")
    rv = client.post(
        "/posting",
        data=dict(organization = "organization",
                    campus = "campus",
                    event = "event",
                    description = "description",
                    date = "date",
                    startTime = 1,
                    endTime = 2,
                    street = "street",
                    city = "city",
                    postal = "postal",
                    commonName = "commonName",
                    college = "college",
                    faculty = "faculty",
                    cost = 20,
                    tags = "tags"),
        follow_redirects=True,
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
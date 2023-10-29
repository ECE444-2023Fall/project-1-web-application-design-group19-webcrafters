import pytest
import sys
sys.path.append('..')

from betula import app  

@pytest.fixture
def client():
    app.config['TESTING'] = True  
    with app.test_client() as client:
        yield client

# Test the userprofile route for name update.
def test_userprofile_update_name(client):
    response = client.post('/userprofile', data={"name": "NewName"})
    assert response.status_code == 200
    assert b'NewName' in response.data 

# Test the userprofile default name when no name is provided.
def test_userprofile_default_name(client):
    response = client.get('/userprofile')
    assert response.status_code == 200
    assert b'Guest' in response.data  

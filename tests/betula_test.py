import pytest

from betula import app

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

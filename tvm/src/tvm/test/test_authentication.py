from .test_main import *

# Get access token
def test_login_200():
    login_data = {
        "username": "test_user",
        "password": "test_pass"
    }

    response = client.post("/token", json=login_data)
    assert response.status_code == 200

def test_login_400():
    login_data = {
        "username": "user400",
        "password": "pass400"
    }

    response = client.post("/token", json=login_data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Incorrect username or password"
    }

# Refresh access token
def test_refresh_access_token_200():
    login = {
        "username": "test_user",
        "password": "test_pass"
    }
    token = client.post("/token", data=login, headers={"Content-Type": "application/x-www-form-urlencoded"})
    refresh_data = {
        "refresh_token": token.json()["refresh_token"],
    }
    response = client.post("/token/refresh", json=refresh_data)

    assert response.status_code == 200

def test_refresh_access_token_401():
    login = {
        "username": "test_user",
        "password": "test_pass"
    }
    token = client.post("/token", data=login, headers={"Content-Type": "application/x-www-form-urlencoded"})
    refresh_data = {
        "refresh_token": token.json()["refresh_token"],
    }

    response = None
    for i in range(0,2):
        response = client.post("/token/refresh", json=refresh_data) # This refreshes the previous token, making the token in refresh_data no longer appear in the database. So when the endpoint gets called a second time, it will return 401.

    assert response.status_code == 401

# Revoke token
def test_revoke_token():
    login = {
        "username": "test_user",
        "password": "test_pass"
    }
    token = client.post("/token", data=login, headers={"Content-Type": "application/x-www-form-urlencoded"})
    refresh_data = {
        "refresh_token": token.json()["refresh_token"],
    }
    response = client.post("/token/revoke", json=refresh_data)

    assert response.status_code == 200

# Log out
def test_logout():
    token = get_token_admin()
    response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

# Create user

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
def test_create_user_200():
    token = get_token_admin()
    response = client.post("/users/?username=newuser&password=newuserpass", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_create_user_400():
    token = get_token_admin()
    response = client.post("/users/?username=test_user&password=test_pass", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Username already registered"
    }

# Read user "me"
def test_read_users_me_admin():
    token = get_token_admin()
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.json() == {
        "username": "test_user",
        "role": "admin"
    }

def test_read_users_me_not_admin():
    token = get_token_not_admin()
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.json() == {
        "username": "test_not_admin",
        "role": "user"
    }

def test_read_users_me_401():
    response = client.get("/me")
    assert response.status_code == 401

# Verify token
def test_verify_user_token_200():
    token = get_token_admin()
    response = client.get(f"/verify-token/{token}", headers = {"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

# Get all users
def test_list_users_200():
    token = get_token_admin()
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "username": "test_user", "role": "admin"},
        {"id": 2, "username": "test_not_admin", "role": "user"}
    ]

def test_list_users_401():
    response = client.get("/users/")
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials"
    }

# Update user by ID
def test_update_user_200():
    updated_data = {
        "username": "updated_username"
    }
    token = get_token_admin()
    response = client.put("/users/1", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_update_user_400():
    updated_data = {
        "username": "test_not_admin"
    }
    token = get_token_admin()
    response = client.put("/users/1", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Username already taken"
    }

def test_update_user_404():
    updated_data = {
        "username": "updated_username"
    }
    token = get_token_admin()
    response = client.put("/users/999", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "User not found"
    }

# Delete user by ID
def test_delete_user_200():
    token = get_token_admin()
    response = client.delete("/users/2", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_delete_user_400():
    token = get_token_admin()
    response = client.delete("/users/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Cannot delete your own account"
    }

def test_delete_user_404():
    token = get_token_admin()
    response = client.delete("/users/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "User not found"
    }
import asyncio

from .test_main import *
from tvm.authentication import get_current_user
from tvm.db import get_db


# Get_current_user
def test_get_current_user_success():
    token = get_token_admin()
    user = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    db_gen = get_db()
    db = next(db_gen)
    try:
        current_user = asyncio.run(get_current_user(token, db))
        assert current_user.username == user.json()["username"]
    finally:
        db_gen.close()


def test_get_current_user_invalid_token():
    token = "invalid_token"
    user = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert user.status_code == 401
    assert user.json()["detail"] == "Kon credentialen niet verifiëren"


def test_get_current_user_no_token():
    user = client.get("/me")

    assert user.status_code == 401
    assert user.json()["detail"] == "Not authenticated"


# Get access token
def test_login_200():
    login_data = {
        "username": "test_user",
        "password": "test_pass"
    }

    response = client.post("/token", data=login_data)
    assert response.status_code == 200


def test_login_400():
    login_data = {
        "username": "user400",
        "password": "pass400"
    }

    response = client.post("/token", data=login_data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Incorrecte gebruikersnaam of wachtwoord"
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
        "detail": "Gebruikersnaam bestaat al!"
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


def test_verify_user_token_403():
    token = "invalid token"
    response = client.get(f"/verify-token/{token}", headers = {"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Token is invalide of verlopen."
    }


# Get all users
def test_list_users_200():
    token = get_token_admin()
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "username": "test_user", "role": "admin"},
        {"id": 2, "username": "test_not_admin", "role": "user"},
        {"id": 3, "username": "user_to_delete", "role": "user"},
    ]


def test_list_users_401():
    response = client.get("/users/")
    assert response.status_code == 401


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
        "detail": "Gebruikersnaam is al in gebruik"
    }


def test_update_user_404():
    updated_data = {
        "username": "updated_username"
    }
    token = get_token_admin()
    response = client.put("/users/999", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Gebruiker niet gevonden"
    }


# Delete user by ID
def test_delete_user_200():
    token = get_token_admin()
    response = client.delete("/users/3", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_delete_user_400():
    token = get_token_admin()
    response = client.delete("/users/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Het is niet mogelijk om je eigen account te verwijderen"
    }


def test_delete_user_404():
    token = get_token_admin()
    response = client.delete("/users/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Gebruiker niet gevonden"
    }


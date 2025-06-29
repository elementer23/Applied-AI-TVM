from fastapi.testclient import TestClient
from tvm.db import reset_database, insert_base_data
import pytest
from tvm.main import app


client = TestClient(app)

def get_token_admin() -> str:
    login = {
        "username": "test_user",
        "password": "test_pass"
    }
    response = client.post("/token", data=login, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200
    return response.json()["access_token"]


def get_token_not_admin() -> str:
    login = {
        "username": "test_not_admin",
        "password": "notadminpass"
    }
    response = client.post("/token", data=login, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200
    return response.json()["access_token"]


# This fixture activates before every test, resetting the database
@pytest.fixture(scope="function", autouse=True)
def prepare_database():
    reset_database()
    insert_base_data()

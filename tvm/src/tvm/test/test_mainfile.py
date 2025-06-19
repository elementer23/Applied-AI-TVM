from .test_main import *


def test_run_without_access_token():
    data = {"input": "Test input"}
    response = client.post("/run",json=data)
    assert response.status_code == 401
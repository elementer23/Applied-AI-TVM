from fastapi.testclient import TestClient

from tvm.main import app

client = TestClient(app)

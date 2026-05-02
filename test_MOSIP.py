from fastapi.testclient import TestClient
from GATE_Auth import app

import json

client = TestClient(app)

def test_user_1():
    with open('mock-data/user-1.json', 'r') as file:
        data = json.load(file)
    response = client.post("/authenticate", json=data)

    assert response.status_code == 200
    assert response.json()["response"]["authStatus"] == True
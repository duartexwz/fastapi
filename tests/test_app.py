from fastapi.testclient import TestClient
from  api.app import app
from http import HTTPStatus


client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"Hello": "World"}





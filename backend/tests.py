from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_main():
    response = client.get('/')
    assert response.status_code == 200


def test_creation_room():
    response = client.post('/', json={'name': 'test', 'password': 'Test12345'})
    assert response.status_code == 302
    assert list(response.json().keys())[0] == 'link'
    assert response.headers['Location'] == response.json()['link'] + '/auth'
    assert response.headers['Content-Type'] == 'application/json'
    assert response.cookies != None


def test_fail_creation_room():
    response = client.post('/', json={'name': 'test', 'password': 'aasfwf'})
    assert response.status_code == 400
    assert response.json()['detail'] == {
        "Code": 400,
        "error": 'password'
    }
    assert response.headers['Content-Type'] == 'application/json'

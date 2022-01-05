from fastapi.testclient import TestClient
from main import app, SECRET_KEY
from utils.crypt import Decoder

"""
The tests should be rewritten but I'm too lazy
"""

client = TestClient(app)
decoder = Decoder(SECRET_KEY)

test_session = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiJDJiJDEyJEF5cmNwRGYvOUhOTDV1UXd0NjguaU8vSkxnN0tnekVrRUNMbXp2LlFaVnJvcDhaTTJQdVQyIiwicGFzc3dvcmQiOiJUZXN0MTIzNDUiLCJ1c2VybmFtZSI6IkFkbWluIn0.EK1sBM5AXioqHqeeeiZzRh0wnm8kaWClvm3pvX_NwBU"


def test_main():
    response = client.get('/')
    assert response.status_code == 200


def test_creation_room():
    response = client.post(
        '/', json={'name': 'test3', 'password': 'Test123456'}
    )
    assert response.status_code == 302
    assert list(response.json().keys())[0] == 'link'
    assert response.headers['Location'] == response.json()['link'] + '/auth'
    assert response.headers['Content-Type'] == 'application/json'


def test_fail_creation_room():
    response = client.post('/', json={'name': 'test', 'password': 'aasfwf'})
    assert response.status_code == 400
    assert response.json()['detail'] == {
        "Code": 400,
        "error": 'password'
    }
    assert response.headers['Content-Type'] == 'application/json'


def test_room_session():
    response = client.get(
        "/rooms/AyrcpDfslash9HNL5uQwt68.iOslashJLg7KgzEkECLmzv.QZVrop8ZM2PuT2",
        cookies={'session': test_session}
    )
    assert response.status_code == 200
    assert response.headers['Connection'] == 'keep-alive'


def test_room_empty_session():
    response = client.get(
        "/rooms/AyrcpDfslash9HNL5uQwt68.iOslashJLg7KgzEkECLmzv.QZVrop8ZM2PuT2",
    )
    assert response.status_code == 401


def test_fail_with_incorrect_session_room_auth():
    response = client.get(
        '/rooms/AyrcpDfslash9HNL5uQwt68.iOslashJLg7KgzEkECLmzv.QZVrop8ZM2PuT2/auth',
        cookies={'session': test_session+'error'}
    )
    assert response.status_code == 400


def test_fail_without_cookies_room_auth():
    response = client.get(
        '/rooms/AyrcpDfslash9HNL5uQwt68.iOslashJLg7KgzEkECLmzv.QZVrop8ZM2PuT2/auth'
    )
    assert response.status_code == 401


def test_password_room_auth():
    response = client.post(
        '/rooms/AyrcpDfslash9HNL5uQwt68.iOslashJLg7KgzEkECLmzv.QZVrop8ZM2PuT2/auth',
        json={"password": "Test12345", "username": "Admin"}
    )
    assert response.status_code == 302
    assert response.cookies.get('session') == test_session


def test_invalid_password_room_auth():
    response = client.post(
        '/rooms/AyrcpDfslash9HNL5uQwt68.iOslashJLg7KgzEkECLmzv.QZVrop8ZM2PuT2/auth',
        json={"password": "Tesadat123456", "username": "Mike"}
    )
    assert response.status_code == 401
    assert response.json() == {'Erorr': 'Invalid password'}

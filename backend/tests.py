from fastapi.testclient import TestClient
from main import app, SECRET_KEY
from utils.crypt import Decoder

client = TestClient(app)
decoder = Decoder(SECRET_KEY)

test_session = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiJDJiJDEyJHNvMy9BcUc0STZpLnc3aGdqdU5KanVyeldlMG1zMXFiNUFCZmFMdHZsOWgxeS92UHVWUW9DIiwicGFzc3dvcmQiOiJUZXN0MTIzNDU2In0.cG6wkGC3Ff6-uDwQw5RfHtIOmu-_dLiUEFQCThB7bQI'


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


def test_room_auth():
    response = client.get(
        '/rooms/so3slashAqG4I6i.w7hgjuNJjurzWe0ms1qb5ABfaLtvl9h1yslashvPuVQoC/auth',
        cookies={'session': test_session}
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


def test_fail_with_incorrect_session_room_auth():
    response = client.get(
        '/rooms/so3slashAqG4I6i.w7hgjuNJjurzWe0ms1qb5ABfaLtvl9h1yslashvPuVQoC/auth',
        cookies={'session': test_session+'error'}
    )
    assert response.status_code == 400


def test_fail_without_cookies_room_auth():
    response = client.get(
        '/rooms/so3slashAqG4I6i.w7hgjuNJjurzWe0ms1qb5ABfaLtvl9h1yslashvPuVQoC/auth'
    )
    assert response.status_code == 401


def test_password_room_auth():
    response = client.post(
        '/rooms/so3slashAqG4I6i.w7hgjuNJjurzWe0ms1qb5ABfaLtvl9h1yslashvPuVQoC/auth',
        json={"password": "Test123456"}
    )
    assert response.status_code == 302
    assert response.cookies.get('session') == test_session


def test_invalid_password_room_auth():
    response = client.post(
        '/rooms/so3slashAqG4I6i.w7hgjuNJjurzWe0ms1qb5ABfaLtvl9h1yslashvPuVQoC/auth',
        json={"password": "Tests123456"}
    )
    assert response.status_code == 401
    assert response.json() == {'Erorr': 'Invalid password'}

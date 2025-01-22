import pytest
from todolist import create_app
import sqlite3

@pytest.fixture()
def app():
    app = create_app(testing=True)
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_nonexistent(client):
    response = client.post('/testpage')
    assert response.status_code == 404

def test_register(client):
    response = client.post('/adduser', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 302
    assert b'<a href="/login">/login</a>. If not, click the link.\n' in response.data

def test_register_duplicate(client):
    client.post('/adduser', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    response = client.post('/adduser', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    assert response.status_code == 302
    assert b'<a href="/register">/register</a>. If not, click the link.\n' in response.data

def test_correct_login(client):
    client.post('/adduser', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    response = client.post('/validation', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    assert response.status_code == 302
    assert b'<a href="/todolist">/todolist</a>. If not, click the link.\n'

def test_incorrect_login(client):
    response = client.post('/validation', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    assert response.status_code == 302
    assert b'<a href="/login">/login</a>. If not, click the link.\n' in response.data

def test_todolist_save(client):
    client.post('/adduser', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    client.post('/validation', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    client.post('/addtask', data={
        'task': 'testtask',
        'description': 'testdesc',
        'due': '11-26-2024 12:40 AM'
    })

    with sqlite3.connect('database.db') as conn:
        result = conn.execute("SELECT * FROM testuser").fetchone()

    assert result == ('testtask', 'testdesc', '11-26-2024 12:40 AM')


if __name__ == '__main__':
    pytest.main()
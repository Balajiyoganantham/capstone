import json
import pytest
import base64
from app import app, db, User  # Assumes your Flask app is in app.py

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Use an in-memory database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "name": "Test User"
    }
    response = client.post('/register', json=payload)
    data = response.get_json()
    assert response.status_code == 201
    assert "User registered successfully" in data['message']

def test_login(client):
    # First, register the user
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "name": "Test User"
    }
    client.post('/register', json=payload)
    
    # Prepare HTTP Basic Auth header (username:password)
    credentials = base64.b64encode(b"testuser:testpassword").decode('utf-8')
    headers = {"Authorization": "Basic " + credentials}
    
    response = client.get('/login', headers=headers)
    data = response.get_json()
    assert response.status_code == 200
    assert "Login successful" in data['message']

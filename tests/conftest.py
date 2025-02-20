import pytest
from app import app, db, User

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        
        with app.app_context():
            db.drop_all()

@pytest.fixture
def auth_headers():
    return {
        'Authorization': 'Basic ' + 'dGVzdHVzZXI6dGVzdHBhc3N3b3Jk'  # testuser:testpassword
    }
import json

def test_register_user(client):
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword',
        'name': 'Test User'
    }
    response = client.post('/register',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 201
    assert b'User registered successfully' in response.data

def test_login_user(client, auth_headers):
    # First register a user
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword',
        'name': 'Test User'
    }
    client.post('/register',
                data=json.dumps(data),
                content_type='application/json')
    
    # Then try to login
    response = client.get('/login', headers=auth_headers)
    assert response.status_code == 200
    assert b'Login successful' in response.data

def test_get_users(client, auth_headers):
    response = client.get('/users', headers=auth_headers)
    assert response.status_code == 200

def test_get_single_user(client, auth_headers):
    # First register a user
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword',
        'name': 'Test User'
    }
    register_response = client.post('/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
    user_id = json.loads(register_response.data)['user']['id']
    
    # Then try to get the user
    response = client.get(f'/users/{user_id}', headers=auth_headers)
    assert response.status_code == 200
    assert json.loads(response.data)['username'] == 'testuser'

def test_update_user(client, auth_headers):
    # First register a user
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword',
        'name': 'Test User'
    }
    register_response = client.post('/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
    user_id = json.loads(register_response.data)['user']['id']
    
    # Then update the user
    update_data = {
        'name': 'Updated Test User'
    }
    response = client.put(f'/users/{user_id}',
                         data=json.dumps(update_data),
                         content_type='application/json',
                         headers=auth_headers)
    assert response.status_code == 200
    assert json.loads(response.data)['user']['name'] == 'Updated Test User'

def test_delete_user(client, auth_headers):
    # First register a user
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword',
        'name': 'Test User'
    }
    register_response = client.post('/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
    user_id = json.loads(register_response.data)['user']['id']
    
    # Then delete the user
    response = client.delete(f'/users/{user_id}', headers=auth_headers)
    assert response.status_code == 200
    assert b'User deleted successfully' in response.data
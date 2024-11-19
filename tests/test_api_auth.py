import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.auth import validate_username, validate_email, validate_password


client = TestClient(app)

@pytest.fixture
def create_user():
    response = client.post("/auth/", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "StrongPassword123!"
    })
    return response

def test_create_user(create_user):
    assert create_user.status_code == 201
    assert create_user.json() is not None

def test_create_user_duplicate_email(create_user):
    response = client.post("/auth/", json={
        "username": "anotheruser",
        "email": "testuser@example.com",  # Email déjà utilisé
        "password": "AnotherStrongPassword123!"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_for_access_token(create_user):
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "StrongPassword123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials():
    response = client.post("/auth/token", data={
        "username": "nonexistentuser",
        "password": "WrongPassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == 'Could not validate user.'

def test_validate_username():
    # Test pour le nom d'utilisateur valide
    valid_username = "valid_username"
    error_message = validate_username(valid_username)
    assert error_message is None

    # Test pour le nom d'utilisateur invalide
    invalid_username = "@invalidusername"
    error_message = validate_username(invalid_username)
    assert error_message == "Le nom d'utilisateur ne doit contenir que des lettres, chiffres et underscores."

def test_validate_email():
    # Test pour l'email valide
    valid_email = "valid@example.com"
    error_message = validate_email(valid_email)
    assert error_message is None

    # Test pour l'email invalide
    invalid_email = "invalid-email"
    error_message = validate_email(invalid_email)
    assert error_message == "L'adresse e-mail n'est pas valide."

def test_validate_password():
    # Test pour le mot de passe valide
    valid_password = "StrongPassword123!"
    error_message = validate_password(valid_password)
    assert error_message is None

    # Test pour le mot de passe invalide (trop court)
    invalid_password = "Short1!"
    error_message = validate_password(invalid_password)
    assert error_message == "Le mot de passe doit contenir au moins 12 caractères."
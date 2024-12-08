import pytest
from curd import app, db, User

@pytest.fixture
def client():
    app.config["TESTING"] = True  # Enable testing mode
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory database

    with app.test_client() as client:  # Creating a test client for making HTTP requests
        with app.app_context():  # Activate the app context for database operations
            db.create_all()  # Create database tables
        yield client  # Provide the test client to the test functions
        with app.app_context():
            db.drop_all()  # Drop all tables after tests are done

# Test for creating a new user
def test_create_user(client):
    response = client.post("/users", json={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200  # Check if the response is successful
    assert response.get_json()["message"] == "New user created"  # Validate the success message

# Test for retrieving all users
def test_get_users(client):
    client.post("/users", json={"username": "test_user_1", "password": "test_password_1"})
    client.post("/users", json={"username": "test_user_2", "password": "test_password_2"})
    response = client.get("/users")  # Retrieve all the users
    data = response.get_json()
    assert response.status_code == 200  # Check the response status
    assert len(data) == 2  # Ensure that 2 users are returned

# Test for retrieving a specific user
def test_get_user(client):
    client.post("/users", json={"username": "test_user", "password": "test_password"})
    response = client.get("/users/1")  # Retrieve the user with user ID 1
    assert response.status_code == 200  # Ensure the response is successful
    assert response.get_json()["username"] == "test_user"  # Verify the username

# Test for updating the user details
def test_update_user(client):
    client.post("/users", json={"username": "test_user", "password": "test_pass"})
    response = client.put("/users/1", json={"username": "test_user_update", "password": "test_password"})
    assert response.status_code == 200  # Check the response status
    assert response.get_json()["message"] == "User details updated"  # Validate the success message

# Test for deleting a user
def test_delete_user(client):
    client.post("/users", json={"username": "test_user", "password": "test_pass"})
    response = client.delete("/users/1")
    assert response.status_code == 200  # Check the response is successful
    assert response.get_json()["message"] == "User Deleted"  # Validate the success message

# Test for creating user with missing fields
def test_create_user_missing_fields(client):
    response = client.post("/users", json={"username": ""})
    assert response.status_code == 400  # Check for bad request status
    assert response.get_json()["error"] == "Please enter username or password."  # Validate the error message

# Test for retrieving a non-existent user
def test_get_nonexistent_user(client):
    response = client.get("/users/896")  # Attempt to retrieve the user with non-existent ID
    assert response.status_code == 404  # Check for the not found status
    assert response.get_json()["error"] == "User not found."  # Validate the error message

def test_signup_success(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "donor@example.com",
            "password": "password123",
            "full_name": "Test Donor",
            "phone": "555-0100",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "donor@example.com"
    assert "access_token" in data


def test_signup_duplicate_email(client):
    payload = {
        "email": "dup@example.com",
        "password": "password123",
        "full_name": "Dup User",
    }
    assert client.post("/auth/signup", json=payload).status_code == 201
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 409
    assert response.json()["code"] == "email_exists"


def test_login_success(client):
    client.post(
        "/auth/signup",
        json={
            "email": "login@example.com",
            "password": "password123",
            "full_name": "Login User",
        },
    )
    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login@example.com"


def test_login_bad_password(client):
    client.post(
        "/auth/signup",
        json={
            "email": "badpass@example.com",
            "password": "password123",
            "full_name": "Bad Pass",
        },
    )
    response = client.post(
        "/auth/login",
        json={"email": "badpass@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


def test_me_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_token(client):
    signup = client.post(
        "/auth/signup",
        json={
            "email": "me@example.com",
            "password": "password123",
            "full_name": "Me User",
        },
    )
    token = signup.json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"

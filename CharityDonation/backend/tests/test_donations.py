def _auth_headers(client, email: str, name: str):
    response = client.post(
        "/auth/signup",
        json={"email": email, "password": "password123", "full_name": name},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_donation(client):
    headers = _auth_headers(client, "donor1@example.com", "Donor One")
    response = client.post(
        "/donations",
        headers=headers,
        json={
            "item_name": "Winter Coat",
            "item_category": "clothes",
            "description": "Warm coat",
            "quantity": 1,
            "pickup_location": {"lat": 16.8, "lng": 96.15},
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["item_name"] == "Winter Coat"
    assert data["status"] in ("pending", "matched")


def test_list_only_own_donations(client):
    headers_a = _auth_headers(client, "donor_a@example.com", "Donor A")
    headers_b = _auth_headers(client, "donor_b@example.com", "Donor B")

    client.post(
        "/donations",
        headers=headers_a,
        json={
            "item_name": "Books",
            "item_category": "stationary",
            "quantity": 2,
            "pickup_location": {"lat": 16.8, "lng": 96.15},
        },
    )
    client.post(
        "/donations",
        headers=headers_b,
        json={
            "item_name": "Food",
            "item_category": "food",
            "quantity": 1,
            "pickup_location": {"lat": 16.81, "lng": 96.16},
        },
    )

    list_a = client.get("/donations", headers=headers_a).json()
    list_b = client.get("/donations", headers=headers_b).json()

    assert len(list_a) == 1
    assert list_a[0]["item_name"] == "Books"
    assert len(list_b) == 1
    assert list_b[0]["item_name"] == "Food"


def test_get_other_users_donation_404(client):
    headers_a = _auth_headers(client, "owner@example.com", "Owner")
    headers_b = _auth_headers(client, "other@example.com", "Other")

    created = client.post(
        "/donations",
        headers=headers_a,
        json={
            "item_name": "Blanket",
            "item_category": "clothes",
            "quantity": 1,
            "pickup_location": {"lat": 16.8, "lng": 96.15},
        },
    ).json()

    response = client.get(f"/donations/{created['id']}", headers=headers_b)
    assert response.status_code == 404

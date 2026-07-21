from app.auth import hash_password
from app.models import User


def test_login_success(client, db_session):
    db_session.add(User(email="a@test.com", password_hash=hash_password("secret123"), role="employee"))
    db_session.commit()
    resp = client.post("/api/auth/login", data={"username": "a@test.com", "password": "secret123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client, db_session):
    db_session.add(User(email="a@test.com", password_hash=hash_password("secret123"), role="employee"))
    db_session.commit()
    resp = client.post("/api/auth/login", data={"username": "a@test.com", "password": "wrong"})
    assert resp.status_code == 401


def test_products_require_auth(client):
    assert client.get("/api/products").status_code == 401


def test_employee_cannot_create_product(client, db_session):
    db_session.add(User(email="emp@test.com", password_hash=hash_password("pw123456"), role="employee"))
    db_session.commit()
    token = client.post(
        "/api/auth/login", data={"username": "emp@test.com", "password": "pw123456"}
    ).json()["access_token"]
    resp = client.post(
        "/api/products",
        json={"name": "Eggs", "price": "3.00", "stock_qty": 10},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
import mongomock
import pytest
from fastapi.testclient import TestClient

from app import db as db_module
from app import sftp_client
from app.main import app


@pytest.fixture
def client(monkeypatch):
    database = mongomock.MongoClient()["test"]
    monkeypatch.setattr(db_module, "get_db", lambda: database)
    with TestClient(app) as c:
        yield c


def login(client, username, password):
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_login_rejects_bad_password(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "nope"})
    assert r.status_code == 401


def test_products_need_auth(client):
    assert client.get("/api/products").status_code == 401


def test_admin_crud(client):
    admin = login(client, "admin", "admin123")
    r = client.post("/api/products", headers=admin,
                    json={"sku": "NEW-1", "name": "New", "price": 1.234})
    assert r.status_code == 201
    pid = r.json()["id"]
    assert r.json()["price"] == 1.23
    assert client.post("/api/products", headers=admin,
                       json={"sku": "NEW-1", "name": "Dup", "price": 1}).status_code == 409
    r = client.put(f"/api/products/{pid}", headers=admin,
                   json={"name": "Renamed", "price": 2, "description": ""})
    assert r.json()["name"] == "Renamed"
    assert client.delete(f"/api/products/{pid}", headers=admin).status_code == 204
    assert client.get(f"/api/products/{pid}", headers=admin).status_code == 404


def test_user_cannot_edit_catalog(client):
    user = login(client, "user", "user123")
    r = client.post("/api/products", headers=user, json={"sku": "X", "name": "X", "price": 1})
    assert r.status_code == 403


def test_cart_flow(client):
    user = login(client, "user", "user123")
    products = client.get("/api/products", headers=user).json()
    mug = next(p for p in products if p["sku"] == "MUG-001")
    client.post("/api/cart/items", headers=user, json={"product_id": mug["id"], "quantity": 2})
    cart = client.post("/api/cart/items", headers=user, json={"product_id": mug["id"]}).json()
    assert cart["item_count"] == 3 and cart["total"] == 28.5
    cart = client.put(f"/api/cart/items/{mug['id']}", headers=user, json={"quantity": 1}).json()
    assert cart["total"] == 9.5
    cart = client.delete(f"/api/cart/items/{mug['id']}", headers=user).json()
    assert cart["items"] == []
    # carts are per user
    other = login(client, "user2", "user123")
    client.post("/api/cart/items", headers=user, json={"product_id": mug["id"]})
    assert client.get("/api/cart", headers=other).json()["item_count"] == 0


def test_ingestion(client, monkeypatch):
    csv_text = (
        "sku,name,price,description\n"
        "MUG-001,Big Mug,12.00,Updated\n"
        "LAMP-001,Desk Lamp,35.50,\n"
        "BAD-1,No price,,\n"
        "BAD-2,Negative,-3,\n"
    )
    monkeypatch.setattr(sftp_client, "read_file", lambda name: csv_text)
    admin = login(client, "admin", "admin123")
    r = client.post("/api/admin/ingest", headers=admin, json={"filename": "x.csv", "replace": True})
    assert r.status_code == 200, r.text
    body = r.json()
    assert (body["created"], body["updated"], body["deleted"]) == (1, 1, 5)
    assert [e["line"] for e in body["errors"]] == [4, 5]
    skus = {p["sku"] for p in client.get("/api/products", headers=admin).json()}
    assert skus == {"MUG-001", "LAMP-001"}
    client.post("/api/admin/reset", headers=admin)
    assert len(client.get("/api/products", headers=admin).json()) == 6


def test_ingestion_rejects_bad_header(client, monkeypatch):
    monkeypatch.setattr(sftp_client, "read_file", lambda name: "foo,bar\n1,2\n")
    admin = login(client, "admin", "admin123")
    r = client.post("/api/admin/ingest", headers=admin, json={"filename": "x.csv"})
    assert r.status_code == 422

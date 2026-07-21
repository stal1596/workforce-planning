def test_sale_decrements_stock(client):
    client.post("/api/products", json={"name": "Milk", "price": "1.20", "stock_qty": 10})
    resp = client.post("/api/sales", json={"product_id": 1, "qty": 3})
    assert resp.status_code == 201
    assert client.get("/api/products").json()[0]["stock_qty"] == 7


def test_sale_rejects_overselling(client):
    client.post("/api/products", json={"name": "Milk", "price": "1.20", "stock_qty": 2})
    resp = client.post("/api/sales", json={"product_id": 1, "qty": 5})
    assert resp.status_code == 422
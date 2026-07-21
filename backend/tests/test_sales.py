def test_sale_decrements_stock(client, admin_headers):
    client.post("/api/products", json={"name": "Milk", "price": "1.20", "stock_qty": 10}, headers=admin_headers)
    resp = client.post("/api/sales", json={"product_id": 1, "qty": 3}, headers=admin_headers)
    assert resp.status_code == 201
    assert client.get("/api/products", headers=admin_headers).json()[0]["stock_qty"] == 7


def test_sale_rejects_overselling(client, admin_headers):
    client.post("/api/products", json={"name": "Milk", "price": "1.20", "stock_qty": 2}, headers=admin_headers)
    resp = client.post("/api/sales", json={"product_id": 1, "qty": 5}, headers=admin_headers)
    assert resp.status_code == 422
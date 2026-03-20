"""
test_products_api.py
--------------------
Tests for the /products/ endpoints.

Run with:
    pytest tests/test_products_api.py -v
"""


class TestListProducts:

    def test_returns_200(self, client):
        res = client.get("/products/")
        assert res.status_code == 200

    def test_returns_seeded_products(self, client):
        res = client.get("/products/")
        assert len(res.json()) == 5

    def test_all_products_are_active(self, client):
        res = client.get("/products/")
        for p in res.json():
            assert p["is_active"] == 1


class TestCreateProduct:

    def test_creates_product_successfully(self, client):
        res = client.post("/products/", json={
            "name": "ensaimada",
            "category": "pastry",
            "unit_cost": 0.90,
        })
        assert res.status_code == 201
        assert res.json()["name"] == "ensaimada"

    def test_product_appears_in_list_after_creation(self, client):
        client.post("/products/", json={"name": "ensaimada", "category": "pastry"})
        names = [p["name"] for p in client.get("/products/").json()]
        assert "ensaimada" in names

    def test_duplicate_name_returns_409(self, client):
        client.post("/products/", json={"name": "ensaimada", "category": "pastry"})
        res = client.post("/products/", json={"name": "ensaimada", "category": "bread"})
        assert res.status_code == 409

    def test_invalid_category_returns_400(self, client):
        res = client.post("/products/", json={
            "name": "test",
            "category": "invalid_category",
        })
        assert res.status_code == 400

    def test_unit_cost_is_optional(self, client):
        res = client.post("/products/", json={"name": "ensaimada", "category": "pastry"})
        assert res.status_code == 201


class TestDeactivateProduct:

    def test_deactivates_product(self, client):
        # Get first product id
        products = client.get("/products/").json()
        product_id = products[0]["product_id"]

        res = client.delete(f"/products/{product_id}")
        assert res.status_code == 200

    def test_deactivated_product_not_in_list(self, client):
        products = client.get("/products/").json()
        product_id = products[0]["product_id"]
        name = products[0]["name"]

        client.delete(f"/products/{product_id}")

        names = [p["name"] for p in client.get("/products/").json()]
        assert name not in names

    def test_deactivate_nonexistent_returns_404(self, client):
        res = client.delete("/products/99999")
        assert res.status_code == 404
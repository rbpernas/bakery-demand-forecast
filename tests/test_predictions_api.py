"""
test_predictions_api.py
-----------------------
Tests for the GET /predictions/ endpoint.

Run with:
    pytest tests/test_predictions_api.py -v
"""


class TestGetPredictions:

    def test_returns_200(self, client):
        res = client.get("/predictions/", params={"target_date": "2024-06-17"})
        assert res.status_code == 200

    def test_returns_list(self, client):
        res = client.get("/predictions/", params={"target_date": "2024-06-17"})
        data = res.json()
        assert isinstance(data, list)

    def test_returns_one_prediction_per_active_product(self, client):
        res = client.get("/predictions/", params={"target_date": "2024-06-17"})
        data = res.json()
        assert len(data) == 5  # matches seed_initial_products

    def test_prediction_has_required_fields(self, client):
        res = client.get("/predictions/", params={"target_date": "2024-06-17"})
        prediction = res.json()[0]
        for field in ("product", "category", "date", "units", "confidence", "observations", "breakdown"):
            assert field in prediction, f"Missing field: {field}"

    def test_units_are_positive(self, client):
        res = client.get("/predictions/", params={"target_date": "2024-06-17"})
        for p in res.json():
            assert p["units"] > 0

    def test_confidence_is_valid_value(self, client):
        res = client.get("/predictions/", params={"target_date": "2024-06-17"})
        valid = {"low", "medium", "high"}
        for p in res.json():
            assert p["confidence"] in valid

    def test_holiday_increases_units(self, client):
        normal  = client.get("/predictions/", params={"target_date": "2024-06-17", "is_holiday": False}).json()
        holiday = client.get("/predictions/", params={"target_date": "2024-06-17", "is_holiday": True}).json()

        normal_total  = sum(p["units"] for p in normal)
        holiday_total = sum(p["units"] for p in holiday)
        assert holiday_total > normal_total

    def test_local_event_increases_units(self, client):
        normal = client.get("/predictions/", params={"target_date": "2024-06-17"}).json()
        event  = client.get("/predictions/", params={"target_date": "2024-06-17", "is_local_event": True}).json()

        assert sum(p["units"] for p in event) > sum(p["units"] for p in normal)

    def test_invalid_date_returns_422(self, client):
        res = client.get("/predictions/", params={"target_date": "not-a-date"})
        assert res.status_code == 422
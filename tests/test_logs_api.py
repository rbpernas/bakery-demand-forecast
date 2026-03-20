"""
test_logs_api.py
----------------
Tests for the /logs/ endpoints.

Run with:
    pytest tests/test_logs_api.py -v
"""

# A valid log payload reused across tests
VALID_LOG = {
    "date":           "2024-06-17",
    "product_id":     1,
    "units_produced": 60,
    "units_sold":     55,
    "units_wasted":   5,
    "sold_out":       False,
    "is_holiday":     False,
    "is_local_event": False,
}


class TestCreateLog:

    def test_creates_log_successfully(self, client):
        res = client.post("/logs/", json=VALID_LOG)
        assert res.status_code == 201

    def test_duplicate_log_returns_409(self, client):
        client.post("/logs/", json=VALID_LOG)
        res = client.post("/logs/", json=VALID_LOG)
        assert res.status_code == 409

    def test_sold_plus_wasted_exceeds_produced_returns_422(self, client):
        bad_log = {**VALID_LOG, "units_sold": 50, "units_wasted": 20}  # 70 > 60
        res = client.post("/logs/", json=bad_log)
        assert res.status_code == 422

    def test_negative_units_returns_422(self, client):
        bad_log = {**VALID_LOG, "units_produced": -1}
        res = client.post("/logs/", json=bad_log)
        assert res.status_code == 422

    def test_optional_fields_accepted(self, client):
        log_with_extras = {
            **VALID_LOG,
            "temperature_max":  22.5,
            "precipitation_mm": 0.0,
            "notes":            "Busy morning",
        }
        res = client.post("/logs/", json=log_with_extras)
        assert res.status_code == 201


class TestGetLogs:

    def test_returns_empty_list_initially(self, client):
        res = client.get("/logs/")
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_saved_log(self, client):
        client.post("/logs/", json=VALID_LOG)
        logs = client.get("/logs/").json()
        assert len(logs) == 1

    def test_filter_by_date_from(self, client):
        client.post("/logs/", json=VALID_LOG)
        # Filter with a date after the log — should return nothing
        res = client.get("/logs/", params={"date_from": "2024-12-31"})
        assert res.json() == []

    def test_filter_by_product_id(self, client):
        client.post("/logs/", json=VALID_LOG)
        res = client.get("/logs/", params={"product_id": 1})
        assert len(res.json()) == 1

    def test_filter_by_wrong_product_id_returns_empty(self, client):
        client.post("/logs/", json=VALID_LOG)
        res = client.get("/logs/", params={"product_id": 99999})
        assert res.json() == []
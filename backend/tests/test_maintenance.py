from fastapi.testclient import TestClient

from database import get_db
from main import app


class FakeQuery:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def delete(self):
        self.db.deleted_models.append(self.model.__tablename__)
        return self.db.row_counts.get(self.model.__tablename__, 0)


class FakeDb:
    def __init__(self):
        self.deleted_models = []
        self.row_counts = {"scores": 2, "criteria": 1, "alternatives": 3}
        self.committed = False

    def query(self, model):
        return FakeQuery(self, model)

    def commit(self):
        self.committed = True


def test_delete_data_requires_confirmation():
    client = TestClient(app)

    response = client.request(
        "DELETE",
        "/api/maintenance/data",
        json={"target": "all", "confirm": "salah"},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "ketik HAPUS untuk konfirmasi"


def test_delete_all_data_removes_scores_criteria_and_alternatives():
    fake_db = FakeDb()

    def override_db():
        yield fake_db

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    try:
        response = client.request(
            "DELETE",
            "/api/maintenance/data",
            json={"target": "all", "confirm": "HAPUS"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_db.deleted_models == ["scores", "criteria", "alternatives"]
    assert fake_db.committed is True
    assert response.json() == {
        "target": "all",
        "deleted": {"scores": 2, "criteria": 1, "alternatives": 3},
    }

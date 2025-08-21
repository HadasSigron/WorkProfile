import sys
import types
import importlib.util
from pathlib import Path
import pytest

@pytest.fixture
def app_module(monkeypatch):
    # 1) מזייפים dbcontext לפני טעינת app.py
    fake_db = types.ModuleType("dbcontext")
    fake_db.health_check = lambda: True
    fake_db.db_data = lambda: [
        {"id": 1, "firstName": "Alice", "lastName": "Doe", "age": 30, "address": "X", "workplace": "Y"}
    ]
    # נחזיר Response מתאים כפי שהאפליקציה מצפה
    sys.modules["dbcontext"] = fake_db

    # 2) טוענים את app.py לפי נתיב (עוקף PYTHONPATH)
    repo_root = Path(__file__).resolve().parents[1]
    app_path = repo_root / "app.py"
    spec = importlib.util.spec_from_file_location("app", app_path)
    app_mod = importlib.util.module_from_spec(spec)
    sys.modules["app"] = app_mod  # לאפשר ייבוא יחסי
    assert spec.loader is not None
    spec.loader.exec_module(app_mod)

    # 3) אחרי טעינת המודול, מחליפים את פונקציות ה-DB במוקים ספציפיים
    def fake_db_add(person):
        return app_mod.Response(status=201)

    def fake_db_delete(_id: int):
        return app_mod.Response(status=204)

    monkeypatch.setattr(app_mod, "db_add", fake_db_add, raising=True)
    monkeypatch.setattr(app_mod, "db_delete", fake_db_delete, raising=True)
    monkeypatch.setattr(app_mod, "db_data", fake_db.db_data, raising=True)

    # 4) לא מרנדרים Jinja בפועל
    monkeypatch.setattr(app_mod, "render_template", lambda *_a, **_k: "OK", raising=True)

    return app_mod


@pytest.fixture
def client(app_module):
    return app_module.app.test_client()


def test_root_ok(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "OK" in resp.get_data(as_text=True)


def test_add_ok(client):
    payload = {
        "firstName": "Bob",
        "lastName": "Smith",
        "age": 25,
        "address": "Somewhere",
        "workplace": "ACME",
    }
    resp = client.post("/add", json=payload)
    assert resp.status_code == 201


def test_add_missing_body_returns_404(client):
    # אין JSON -> בקוד שלך זה מחזיר 404
    resp = client.post("/add", data="", content_type="application/json")
    assert resp.status_code == 404


def test_delete_ok(client):
    resp = client.delete("/delete/1")
    assert resp.status_code == 204


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200

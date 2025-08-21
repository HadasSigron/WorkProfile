import sys
import types
import importlib
import pytest

@pytest.fixture
def app_module(monkeypatch):
    # מכניסים מודול dbcontext מזויף ל-sys.modules לפני ה-import של app
    fake_db = types.ModuleType("dbcontext")
    fake_db.health_check = lambda: True
    # שמים מצייני מקום לשאר הפונקציות; נחליף אותן אחרי import
    fake_db.db_data = lambda: []
    fake_db.db_add = lambda person: None
    fake_db.db_delete = lambda _id: None

    sys.modules["dbcontext"] = fake_db

    # אם app כבר מוטען, נוריד אותו כדי לייבא מחדש עם ה-fake
    if "app" in sys.modules:
        del sys.modules["app"]

    app_mod = importlib.import_module("app")

    # כעת נחליף את הפונקציות במרחב של מודול app לפונקציות מזויפות "אמיתיות"
    def fake_db_data():
        return [
            {"id": 1, "firstName": "Alice", "lastName": "Doe", "age": 30, "address": "X", "workplace": "Y"}
        ]

    def fake_db_add(person):
        # מחזיר Response 201 כמו API תקין
        return app_mod.Response(status=201)

    def fake_db_delete(_id: int):
        # מחזיר Response 204
        return app_mod.Response(status=204)

    monkeypatch.setattr(app_mod, "db_data", fake_db_data, raising=True)
    monkeypatch.setattr(app_mod, "db_add", fake_db_add, raising=True)
    monkeypatch.setattr(app_mod, "db_delete", fake_db_delete, raising=True)

    # לא רוצים באמת לרנדר קובץ תבנית - מחליפים render_template להחזיר טקסט
    monkeypatch.setattr(app_mod, "render_template", lambda *_args, **_kw: "OK", raising=True)

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
    # ללא JSON כלל → בקוד שלך זה אמור להחזיר 404
    resp = client.post("/add", data="", content_type="application/json")
    assert resp.status_code == 404


def test_delete_ok(client):
    resp = client.delete("/delete/1")
    assert resp.status_code == 204


def test_health_exists_and_ok(client):
    # בהנחה שיש ראוט /health שמחזיר 200
    resp = client.get("/health")
    assert resp.status_code == 200

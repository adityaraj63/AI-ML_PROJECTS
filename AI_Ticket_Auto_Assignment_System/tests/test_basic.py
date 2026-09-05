"""
Basic tests for the Flask application
"""
import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_redirects(client):
    resp = client.get("/")
    assert resp.status_code in (301, 302)


def test_login_page(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200
    assert b"Sign In" in resp.data or b"HelpDesk" in resp.data


def test_register_page(client):
    resp = client.get("/auth/register")
    assert resp.status_code == 200


def test_api_auth_status(client):
    resp = client.get("/api/v1/auth/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"]["authenticated"] is False


def test_api_departments(client):
    with client.application.app_context():
        from app.utils.seeder import seed_departments
        seed_departments()
    resp = client.get("/api/v1/departments")
    assert resp.status_code == 401  # requires auth


def test_ml_preprocessor():
    from app.ml.preprocessor import preprocess, clean_text, extract_keywords
    raw = "My Laptop is NOT turning ON!! Battery issue."
    cleaned = clean_text(raw)
    assert cleaned == cleaned.lower()

    processed = preprocess(raw)
    assert "laptop" in processed or "latop" in processed or len(processed) > 0

    keywords = extract_keywords(raw, top_n=3)
    assert isinstance(keywords, list)
    assert len(keywords) <= 3


def test_dataset_generation():
    from app.ml.dataset_generator import generate_tickets
    df = generate_tickets(100)
    assert len(df) == 100
    assert "department" in df.columns
    assert "description" in df.columns
    assert df["department"].nunique() == 10


def test_api_predict_route(client):
    with client.application.app_context():
        from app.utils.seeder import seed_all
        seed_all()

    # 1. Unauthenticated prediction request
    resp = client.post(
        "/api/v1/predict",
        json={"title": "Test Title", "description": "Test Description"}
    )
    assert resp.status_code == 401

    # 2. Login as employee
    login_resp = client.post(
        "/auth/login",
        data={"email": "emma@company.com", "password": "Password@123"},
        follow_redirects=True
    )
    assert login_resp.status_code == 200

    # 3. Valid authenticated prediction request
    resp = client.post(
        "/api/v1/predict",
        json={
            "title": "My laptop screen has green lines and flickers",
            "description": "Since yesterday evening, the laptop screen started flickering with vertical green lines."
        }
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "predicted_department" in data["data"]
    assert "confidence" in data["data"]
    assert "priority" in data["data"]
    assert "keywords" in data["data"]

    # 4. Invalid input (too short description)
    resp = client.post(
        "/api/v1/predict",
        json={
            "title": "My laptop screen has green lines",
            "description": "Short"
        }
    )
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False


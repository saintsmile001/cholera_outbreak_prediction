"""
Comprehensive API test suite.

Tests all endpoints, edge cases, validation, and response schemas.
Run with: pytest tests/ -v
"""

from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app

# Create tables for testing environment
Base.metadata.create_all(bind=engine)

client = TestClient(app)



# ═══════════════════════════════════════════════════════════════════════════
# Root
# ═══════════════════════════════════════════════════════════════════════════

class TestRoot:
    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_docs_link(self):
        data = client.get("/").json()
        assert "docs" in data
        assert data["docs"] == "/docs"

    def test_root_contains_version(self):
        data = client.get("/").json()
        assert "version" in data


# ═══════════════════════════════════════════════════════════════════════════
# Health
# ═══════════════════════════════════════════════════════════════════════════

class TestHealth:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_status_is_healthy(self):
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_health_includes_version(self):
        data = client.get("/health").json()
        assert "version" in data

    def test_health_includes_model_status(self):
        data = client.get("/health").json()
        assert "model_status" in data


# ═══════════════════════════════════════════════════════════════════════════
# Prediction
# ═══════════════════════════════════════════════════════════════════════════

VALID_PAYLOAD = {
    "location": "Maiduguri",
    "rainfall": 125.0,
    "population": 150000,
    "population_density": 5000,
    "wash_score": 0.2,
    "conflict_score": 0.8,
    "idp_camp": True,
    "month": 8,
}


class TestPrediction:
    def test_predict_returns_200(self):
        response = client.post("/api/v1/predict", json=VALID_PAYLOAD)
        assert response.status_code == 200

    def test_predict_returns_risk_level(self):
        data = client.post("/api/v1/predict", json=VALID_PAYLOAD).json()
        assert "risk_level" in data
        assert data["risk_level"] in ("high", "moderate", "low")

    def test_predict_returns_probability(self):
        data = client.post("/api/v1/predict", json=VALID_PAYLOAD).json()
        assert "probability" in data
        assert 0 <= data["probability"] <= 1

    def test_predict_returns_location(self):
        data = client.post("/api/v1/predict", json=VALID_PAYLOAD).json()
        assert data["location"] == "Maiduguri"

    def test_predict_returns_contributing_factors(self):
        data = client.post("/api/v1/predict", json=VALID_PAYLOAD).json()
        assert "contributing_factors" in data
        assert isinstance(data["contributing_factors"], list)
        assert len(data["contributing_factors"]) > 0

    def test_predict_returns_explanation(self):
        data = client.post("/api/v1/predict", json=VALID_PAYLOAD).json()
        assert "explanation" in data
        assert len(data["explanation"]) > 10

    def test_predict_returns_prediction_method(self):
        data = client.post("/api/v1/predict", json=VALID_PAYLOAD).json()
        assert data["prediction_method"] in ("rule-based", "ml-model")

    def test_predict_low_risk_scenario(self):
        payload = {
            "location": "Shani",
            "rainfall": 10.0,
            "population": 20000,
            "population_density": 200,
            "wash_score": 0.9,
            "conflict_score": 0.1,
            "idp_camp": False,
            "month": 2,
        }
        data = client.post("/api/v1/predict", json=payload).json()
        assert data["risk_level"] == "low"
        assert data["probability"] < 0.4

    def test_predict_high_risk_scenario(self):
        payload = {
            "location": "Bama",
            "rainfall": 200.0,
            "population": 500000,
            "population_density": 9000,
            "wash_score": 0.05,
            "conflict_score": 0.95,
            "idp_camp": True,
            "month": 8,
        }
        data = client.post("/api/v1/predict", json=payload).json()
        assert data["risk_level"] == "high"
        assert data["probability"] >= 0.7

    def test_predict_rejects_negative_rainfall(self):
        payload = {**VALID_PAYLOAD, "rainfall": -10}
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_predict_rejects_invalid_month(self):
        payload = {**VALID_PAYLOAD, "month": 13}
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_predict_rejects_wash_score_above_1(self):
        payload = {**VALID_PAYLOAD, "wash_score": 1.5}
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_predict_rejects_empty_location(self):
        payload = {**VALID_PAYLOAD, "location": ""}
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_predict_rejects_missing_fields(self):
        response = client.post("/api/v1/predict", json={"location": "Test"})
        assert response.status_code == 422

    def test_predict_rejects_empty_body(self):
        response = client.post("/api/v1/predict", json={})
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════
# Analytics
# ═══════════════════════════════════════════════════════════════════════════

class TestAnalytics:
    def test_summary_returns_200(self):
        response = client.get("/api/v1/analytics/summary")
        assert response.status_code == 200

    def test_summary_contains_counts(self):
        data = client.get("/api/v1/analytics/summary").json()
        assert "total_lgas" in data
        assert data["total_lgas"] == 27
        assert "high_risk_count" in data
        assert "moderate_risk_count" in data
        assert "low_risk_count" in data

    def test_summary_counts_add_up(self):
        data = client.get("/api/v1/analytics/summary").json()
        total = data["high_risk_count"] + data["moderate_risk_count"] + data["low_risk_count"]
        assert total == data["total_lgas"]

    def test_summary_with_month_param(self):
        response = client.get("/api/v1/analytics/summary?month=1")
        assert response.status_code == 200

    def test_summary_rejects_invalid_month(self):
        response = client.get("/api/v1/analytics/summary?month=15")
        assert response.status_code == 422

    def test_trends_returns_200(self):
        response = client.get("/api/v1/analytics/trends")
        assert response.status_code == 200

    def test_trends_has_12_months(self):
        data = client.get("/api/v1/analytics/trends").json()
        assert len(data["trend"]) == 12

    def test_trends_with_location_param(self):
        response = client.get("/api/v1/analytics/trends?location=Bama")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Bama"

    def test_high_risk_returns_200(self):
        response = client.get("/api/v1/analytics/high-risk")
        assert response.status_code == 200

    def test_high_risk_structure(self):
        data = client.get("/api/v1/analytics/high-risk").json()
        assert "count" in data
        assert "lgas" in data
        assert isinstance(data["lgas"], list)

    def test_high_risk_lgas_are_sorted(self):
        data = client.get("/api/v1/analytics/high-risk").json()
        probabilities = [lga["probability"] for lga in data["lgas"]]
        assert probabilities == sorted(probabilities, reverse=True)

    def test_lgas_returns_200(self):
        response = client.get("/api/v1/analytics/lgas")
        assert response.status_code == 200

    def test_lgas_returns_27(self):
        data = client.get("/api/v1/analytics/lgas").json()
        assert data["count"] == 27
        assert len(data["lgas"]) == 27


# ═══════════════════════════════════════════════════════════════════════════
# Datasets
# ═══════════════════════════════════════════════════════════════════════════

class TestDatasets:
    def test_datasets_returns_200(self):
        response = client.get("/api/v1/datasets")
        assert response.status_code == 200

    def test_datasets_lists_artifacts(self):
        data = client.get("/api/v1/datasets").json()
        assert "datasets" in data
        assert len(data["datasets"]) == 2

    def test_dataset_has_metadata(self):
        data = client.get("/api/v1/datasets").json()
        for ds in data["datasets"]:
            assert "name" in ds
            assert "path" in ds
            assert "exists" in ds


# ═══════════════════════════════════════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════════════════════════════════════

import uuid


def _unique_user():
    """Generate unique user details for test isolation."""
    uid = uuid.uuid4().hex[:8]
    return {
        "email": f"test_{uid}@example.com",
        "username": f"test_{uid}",
        "full_name": "Test User",
        "password": "SecureP@ss123",
    }


def _register_and_login(user_data: dict | None = None) -> tuple[dict, str]:
    """Helper: register a user and return (user_data, access_token)."""
    user = user_data or _unique_user()
    client.post("/api/v1/auth/register", json=user)
    login_resp = client.post("/api/v1/auth/login", json={
        "email": user["email"],
        "password": user["password"],
    })
    token = login_resp.json()["access_token"]
    return user, token


class TestAuthRegister:
    def test_register_returns_201(self):
        user = _unique_user()
        response = client.post("/api/v1/auth/register", json=user)
        assert response.status_code == 201

    def test_register_returns_user_profile(self):
        user = _unique_user()
        data = client.post("/api/v1/auth/register", json=user).json()
        assert data["email"] == user["email"]
        assert data["username"] == user["username"]
        assert data["full_name"] == user["full_name"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_register_rejects_duplicate_email(self):
        user = _unique_user()
        client.post("/api/v1/auth/register", json=user)
        # Same email, different username
        duplicate = {**user, "username": f"other_{uuid.uuid4().hex[:8]}"}
        response = client.post("/api/v1/auth/register", json=duplicate)
        assert response.status_code == 409

    def test_register_rejects_duplicate_username(self):
        user = _unique_user()
        client.post("/api/v1/auth/register", json=user)
        # Same username, different email
        duplicate = {**user, "email": f"other_{uuid.uuid4().hex[:8]}@example.com"}
        response = client.post("/api/v1/auth/register", json=duplicate)
        assert response.status_code == 409

    def test_register_rejects_short_password(self):
        user = _unique_user()
        user["password"] = "short"
        response = client.post("/api/v1/auth/register", json=user)
        assert response.status_code == 422

    def test_register_rejects_invalid_username(self):
        user = _unique_user()
        user["username"] = "invalid user!"  # spaces and special chars
        response = client.post("/api/v1/auth/register", json=user)
        assert response.status_code == 422

    def test_register_rejects_missing_fields(self):
        response = client.post("/api/v1/auth/register", json={"email": "a@b.com"})
        assert response.status_code == 422


class TestAuthLogin:
    def test_login_returns_200_and_token(self):
        user = _unique_user()
        client.post("/api/v1/auth/register", json=user)
        response = client.post("/api/v1/auth/login", json={
            "email": user["email"],
            "password": user["password"],
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_rejects_wrong_password(self):
        user = _unique_user()
        client.post("/api/v1/auth/register", json=user)
        response = client.post("/api/v1/auth/login", json={
            "email": user["email"],
            "password": "WrongPassword99",
        })
        assert response.status_code == 401

    def test_login_rejects_nonexistent_email(self):
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@nowhere.com",
            "password": "anything",
        })
        assert response.status_code == 401


class TestAuthMe:
    def test_me_returns_profile(self):
        user, token = _register_and_login()
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user["email"]
        assert data["username"] == user["username"]

    def test_me_rejects_no_token(self):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_me_rejects_invalid_token(self):
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalidtoken123",
        })
        assert response.status_code == 401


class TestAuthLogout:
    def test_logout_succeeds(self):
        _, token = _register_and_login()
        response = client.post("/api/v1/auth/logout", headers={
            "Authorization": f"Bearer {token}",
        })
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

    def test_token_rejected_after_logout(self):
        _, token = _register_and_login()
        client.post("/api/v1/auth/logout", headers={
            "Authorization": f"Bearer {token}",
        })
        # Using the same token should now fail
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert response.status_code == 401


class TestAuthChangePassword:
    def test_change_password_succeeds(self):
        user, token = _register_and_login()
        response = client.post("/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": user["password"],
                "new_password": "NewSecureP@ss456",
            },
        )
        assert response.status_code == 200

    def test_login_works_with_new_password(self):
        user, token = _register_and_login()
        client.post("/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": user["password"],
                "new_password": "NewSecureP@ss456",
            },
        )
        # Login with new password
        response = client.post("/api/v1/auth/login", json={
            "email": user["email"],
            "password": "NewSecureP@ss456",
        })
        assert response.status_code == 200

    def test_change_password_rejects_wrong_current(self):
        _, token = _register_and_login()
        response = client.post("/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "WrongPassword99",
                "new_password": "NewSecureP@ss456",
            },
        )
        assert response.status_code == 401


class TestAuthForgotResetPassword:
    def test_forgot_password_returns_token(self):
        user = _unique_user()
        client.post("/api/v1/auth/register", json=user)
        response = client.post("/api/v1/auth/forgot-password", json={
            "email": user["email"],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["reset_token"] is not None

    def test_forgot_password_unknown_email_still_200(self):
        response = client.post("/api/v1/auth/forgot-password", json={
            "email": "nobody@nowhere.com",
        })
        # Should not reveal whether the email exists
        assert response.status_code == 200
        data = response.json()
        assert data["reset_token"] is None

    def test_reset_password_works(self):
        user = _unique_user()
        client.post("/api/v1/auth/register", json=user)
        # Get reset token
        forgot_resp = client.post("/api/v1/auth/forgot-password", json={
            "email": user["email"],
        })
        reset_token = forgot_resp.json()["reset_token"]
        # Reset password
        response = client.post("/api/v1/auth/reset-password", json={
            "token": reset_token,
            "new_password": "ResetP@ssword789",
        })
        assert response.status_code == 200
        # Login with new password
        login_resp = client.post("/api/v1/auth/login", json={
            "email": user["email"],
            "password": "ResetP@ssword789",
        })
        assert login_resp.status_code == 200

    def test_reset_password_rejects_invalid_token(self):
        response = client.post("/api/v1/auth/reset-password", json={
            "token": "invalidtoken",
            "new_password": "NewP@ssword123",
        })
        assert response.status_code == 401


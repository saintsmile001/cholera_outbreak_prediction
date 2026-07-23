"""
Tests for dataset-based prediction API endpoints.
"""

import io
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDatasetPrediction:
    def test_predict_dataset_returns_200(self):
        response = client.get("/api/v1/predict/dataset?limit=20")
        assert response.status_code == 200
        data = response.json()
        assert "dataset_name" in data
        assert "total_records_processed" in data
        assert data["total_records_processed"] > 0
        assert "lgas_present" in data
        assert isinstance(data["lgas_present"], list)
        assert len(data["lgas_present"]) > 0
        assert "summary_by_lga" in data
        assert "all_predictions" in data

    def test_predict_dataset_filter_by_location(self):
        response = client.get("/api/v1/predict/dataset?location=Maiduguri&limit=20")
        assert response.status_code == 200
        data = response.json()
        assert data["lgas_present"] == ["Maiduguri"]
        for item in data["all_predictions"]:
            assert item["location"].lower() == "maiduguri"

    def test_predict_dataset_by_lga_path(self):
        response = client.get("/api/v1/predict/dataset/lga/Bama?limit=15")
        assert response.status_code == 200
        data = response.json()
        assert data["lgas_present"] == ["Bama"]
        assert len(data["summary_by_lga"]) == 1
        assert data["summary_by_lga"][0]["location"] == "Bama"

    def test_predict_dataset_with_month_filter(self):
        response = client.get("/api/v1/predict/dataset?month=8&limit=20")
        assert response.status_code == 200
        data = response.json()
        for item in data["all_predictions"]:
            assert item["month"] == 8

    def test_predict_uploaded_csv_dataset(self):
        csv_content = (
            "Year,Week,Month,LGA,Rainfall_mm,Population_Density,Safe_Water_pct,IDP_Population,Conflict_Score\n"
            "2025,10,8,Maiduguri,180.0,6000,25,12000,0.7\n"
            "2025,10,8,Bama,220.0,4000,15,25000,0.9\n"
            "2025,10,8,Jere,140.0,4500,30,8000,0.5\n"
        )
        files = {
            "file": ("test_outbreak_data.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
        }
        response = client.post("/api/v1/predict/dataset/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["dataset_name"] == "test_outbreak_data.csv"
        assert data["total_records_processed"] == 3
        assert set(data["lgas_present"]) == {"Bama", "Jere", "Maiduguri"}
        assert len(data["summary_by_lga"]) == 3

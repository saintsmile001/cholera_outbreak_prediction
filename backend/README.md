# AI-Powered Cholera Outbreak Prediction API

A production-grade FastAPI backend for predicting cholera outbreak risk in **Borno State, Nigeria**.

The system combines environmental indicators (rainfall, sanitation scores), demographic data (population, density, IDP camp presence), and conflict metrics to estimate outbreak probability across all 27 Local Government Areas.

---

## Quick Start

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create virtual environment
python -m venv .venv

# 3. Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the development server
uvicorn app.main:app --reload
```

The API will be available at **http://127.0.0.1:8000**

### Documentation

| URL | Description |
|-----|-------------|
| `/docs` | Swagger UI (interactive) |
| `/redoc` | ReDoc (read-only) |
| `/health` | Health check |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check + model status |
| `POST` | `/api/v1/predict` | Predict cholera outbreak risk |
| `GET` | `/api/v1/analytics/summary` | Dashboard summary for all LGAs |
| `GET` | `/api/v1/analytics/trends` | Monthly risk trend for a location |
| `GET` | `/api/v1/analytics/high-risk` | High/moderate risk LGAs |
| `GET` | `/api/v1/analytics/lgas` | List all 27 Borno LGAs |
| `GET` | `/api/v1/datasets` | Available model artifacts |

### Example Prediction Request

```bash
curl -X POST http://127.0.0.1:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Maiduguri",
    "rainfall": 125.0,
    "population": 150000,
    "population_density": 5000,
    "wash_score": 0.2,
    "conflict_score": 0.8,
    "idp_camp": true,
    "month": 8
  }'
```

### Example Response

```json
{
  "location": "Maiduguri",
  "risk_level": "high",
  "probability": 0.742,
  "confidence": 0.903,
  "model_version": "1.0.0",
  "prediction_method": "rule-based",
  "contributing_factors": [
    { "factor": "Rainfall intensity", "value": 1.0, "impact": "high" },
    { "factor": "Poor sanitation (WASH deficit)", "value": 0.8, "impact": "high" },
    { "factor": "Conflict / insurgency pressure", "value": 0.8, "impact": "high" }
  ],
  "explanation": "Risk score combines rainfall, sanitation conditions..."
}
```

---

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── analytics.py     # Summary, trends, high-risk endpoints
│   │   │   ├── datasets.py      # Model artifact metadata
│   │   │   ├── health.py        # Health check
│   │   │   └── prediction.py    # POST /predict
│   │   └── router.py            # Central router aggregation
│   │
│   ├── core/
│   │   ├── config.py            # Pydantic Settings (loads .env)
│   │   ├── constants.py         # Risk levels, LGA names, weights
│   │   ├── exceptions.py        # Custom exceptions + handlers
│   │   └── logger.py            # Structured logging
│   │
│   ├── ml/
│   │   ├── model_loader.py      # ModelManager (loads .joblib)
│   │   ├── predictor.py         # Rule-based + ML prediction
│   │   └── preprocessing.py     # Feature normalisation
│   │
│   ├── models/
│   │   ├── request_models.py    # Pydantic request schemas
│   │   └── response_models.py   # Pydantic response schemas
│   │
│   ├── services/
│   │   ├── analytics_service.py # Dashboard analytics logic
│   │   └── prediction_service.py# Prediction business logic
│   │
│   ├── utils/
│   │   ├── constants.py         # Re-exports core constants
│   │   └── helpers.py           # General utilities
│   │
│   ├── __init__.py
│   └── main.py                  # App entry point
│
├── models/
│   ├── cholera_model.joblib
│   └── preprocessor.joblib
│
├── tests/
│   └── test_api.py
│
├── .env
├── requirements.txt
└── README.md
```

---

## Configuration

All settings are loaded from the `.env` file via `app.core.config`:

```env
APP_NAME=AI-Powered Cholera Outbreak Prediction API
APP_VERSION=1.0.0
API_PREFIX=/api/v1
DEBUG=True
HOST=127.0.0.1
PORT=8000
MODEL_PATH=models/cholera_model.joblib
PREPROCESSOR_PATH=models/preprocessor.joblib
```

---

## Testing

```bash
cd backend
pytest tests/ -v
```

---

## Technology Stack

- **Framework**: FastAPI
- **Validation**: Pydantic v2
- **ML**: scikit-learn + joblib
- **Server**: Uvicorn
- **Testing**: pytest

---

## License

This project is developed as part of an AI/ML group project focused on public health prediction.

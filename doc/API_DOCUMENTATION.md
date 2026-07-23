# Cholera Outbreak Prediction System — Frontend API Documentation

Welcome to the official API documentation for the **Cholera Outbreak Prediction System**. This document provides full specification and integration details for frontend developers building client applications (Web, Mobile, or Dashboards).

---

## 1. Overview & Setup

### Base URL
- **Local Development**: `http://127.0.0.1:8000` (or `http://localhost:8000`)
- **Staging / Production**: `https://<your-railway-or-heroku-app>.up.railway.app`

### Common Headers
| Header Name | Value | Required | Description |
|---|---|---|---|
| `Content-Type` | `application/json` | Yes | Required for all `POST` requests |
| `Authorization` | `Bearer <JWT_ACCESS_TOKEN>` | Conditional | Required for protected endpoints (e.g. `/api/v1/auth/me`, `/logout`) |

---

## 2. Risk Prediction API

### `POST /api/v1/predict`
Evaluates environmental, demographic, and WASH indicators for a specified Local Government Area (LGA) in Borno State and returns an outbreak risk score, probability, risk classification, and contributing factors.

> [!IMPORTANT]
> **Field Update Notice for Frontend Developers**:
> The `conflict_score` field is **OPTIONAL**. If your frontend form does not capture or send `conflict_score`, you can safely omit `"conflict_score"` from the request payload. The backend will default `conflict_score` to `0.0`.

#### Request Headers
```http
Content-Type: application/json
```

#### Request Payload (`PredictionRequest`)
| Field Name | Type | Required | Constraints | Description & Examples |
|---|---|---|---|---|
| `location` | `string` | **Yes** | 1–100 chars | Name of LGA in Borno State (e.g., `"Maiduguri"`, `"Bama"`, `"Jere"`) |
| `rainfall` | `number` | **Yes** | `ge=0`, `le=1000` | Rainfall in millimetres over reference period (e.g. `125.0`) |
| `population` | `integer` | **Yes** | `ge=0`, `le=10000000` | Total population of the LGA (e.g. `150000`) |
| `population_density` | `number` | **Yes** | `ge=0`, `le=100000` | Population density in people per km² (e.g. `5000.0`) |
| `wash_score` | `number` | **Yes** | `0.0` to `1.0` | Water, Sanitation & Hygiene index (0 = worst, 1 = best) (e.g. `0.2`) |
| `month` | `integer` | **Yes** | `1` to `12` | Month of year (1 = January ... 12 = December) (e.g. `8`) |
| `idp_camp` | `boolean` | Optional | `default: false` | Whether an Internally Displaced Persons camp is present (`true`/`false`) |
| `conflict_score` | `number` | **Optional** | `0.0` to `1.0`, `default: 0.0` | Conflict/insurgency pressure. **May be omitted by frontend.** |

#### Example Request (Standard Frontend Payload — without `conflict_score`)
```json
{
  "location": "Maiduguri",
  "rainfall": 125.0,
  "population": 150000,
  "population_density": 5000.0,
  "wash_score": 0.2,
  "idp_camp": true,
  "month": 8
}
```

#### Example Request (With `conflict_score` if available)
```json
{
  "location": "Maiduguri",
  "rainfall": 125.0,
  "population": 150000,
  "population_density": 5000.0,
  "wash_score": 0.2,
  "conflict_score": 0.8,
  "idp_camp": true,
  "month": 8
}
```

#### Response Body (`PredictionResponse`) — Status `200 OK`
```json
{
  "location": "Maiduguri",
  "risk_level": "high",
  "probability": 0.742,
  "confidence": 0.903,
  "model_version": "1.0.0",
  "prediction_method": "rule-based",
  "contributing_factors": [
    {
      "factor": "Rainfall intensity",
      "value": 0.3125,
      "impact": "high"
    },
    {
      "factor": "Poor sanitation (WASH deficit)",
      "value": 0.8,
      "impact": "high"
    },
    {
      "factor": "High population density",
      "value": 0.5,
      "impact": "moderate"
    },
    {
      "factor": "Presence of IDP camp",
      "value": 1.0,
      "impact": "high"
    }
  ],
  "explanation": "High risk of cholera outbreak in Maiduguri (probability: 74.2%). Primary contributing factors: Poor sanitation (WASH deficit), Presence of IDP camp, Rainfall intensity."
}
```

#### Response Field Reference
| Field Name | Type | Description |
|---|---|---|
| `location` | `string` | Assessed LGA location |
| `risk_level` | `string` | Classification: `"high"`, `"moderate"`, or `"low"` |
| `probability` | `number` | Calculated outbreak probability score between `0.0` and `1.0` |
| `confidence` | `number` | Model confidence metric (0.0 to 1.0) |
| `model_version` | `string` | Version of prediction model used |
| `prediction_method` | `string` | Assessment model engine (`"ml-model"` or `"rule-based"`) |
| `contributing_factors` | `array` | List of items containing `{ factor, value, impact }` |
| `explanation` | `string` | Formatted summary text suitable for display in UI |

---

## 2.1 Dataset-Based Risk Prediction API

### `GET /api/v1/predict/dataset`
Runs outbreak risk predictions across records in the dataset (`Borno_Cholera_Hackathon_2017_2026.csv`). Groups and returns predictions organized by Local Government Area (LGA).

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `location` | `string` | No | `null` | Filter predictions by Local Government Area (e.g., `"Maiduguri"`, `"Bama"`) |
| `month` | `integer` | No | `null` | Filter predictions by month (1 to 12) |
| `year` | `integer` | No | `null` | Filter predictions by year (e.g. 2024, 2025) |
| `limit` | `integer` | No | `200` | Maximum dataset records to evaluate (1 to 2000) |

#### Example Request
```http
GET /api/v1/predict/dataset?location=Maiduguri&month=8&limit=50
```

#### Response Body (`DatasetPredictionResponse`) — Status `200 OK`
```json
{
  "dataset_name": "Borno_Cholera_Hackathon_2017_2026.csv",
  "total_records_processed": 10,
  "lgas_present": [
    "Maiduguri"
  ],
  "summary_by_lga": [
    {
      "location": "Maiduguri",
      "total_records": 10,
      "average_probability": 0.735,
      "max_probability": 0.812,
      "highest_risk_level": "high",
      "predictions": [
        {
          "year": 2024,
          "week": 32,
          "month": 8,
          "location": "Maiduguri",
          "rainfall": 145.0,
          "population_density": 5200.0,
          "wash_score": 0.25,
          "risk_level": "high",
          "probability": 0.765,
          "confidence": 0.895,
          "prediction_method": "rule-based",
          "contributing_factors": [
            { "factor": "Rainfall intensity", "value": 0.3625, "impact": "high" },
            { "factor": "Poor sanitation (WASH deficit)", "value": 0.75, "impact": "high" }
          ],
          "explanation": "High risk of cholera outbreak in Maiduguri..."
        }
      ]
    }
  ],
  "all_predictions": [...]
}
```

---

### `GET /api/v1/predict/dataset/lga/{lga_name}`
Retrieves dataset-driven risk predictions specifically for a named Local Government Area (LGA) present in the dataset.

#### Example Request
```http
GET /api/v1/predict/dataset/lga/Bama?month=8
```

---

### `POST /api/v1/predict/dataset/upload`
Uploads a custom CSV dataset file to calculate risk predictions using the model, returning predictions organized per Local Government Area present in the uploaded file.

#### Example Request (Multipart Form Data)
```http
POST /api/v1/predict/dataset/upload
Content-Type: multipart/form-data; boundary=---------------------------974767299852498929531610575

-----------------------------974767299852498929531610575
Content-Disposition: form-data; name="file"; filename="my_lga_data.csv"
Content-Type: text/csv

Year,Week,Month,LGA,Rainfall_mm,Population_Density,Safe_Water_pct,IDP_Population,Conflict_Score
2025,32,8,Maiduguri,150.0,5000,20,10000,0.8
2025,32,8,Bama,190.0,3500,15,22000,0.9
-----------------------------974767299852498929531610575--
```

---

## 3. Analytics & Dashboard API


### `GET /api/v1/analytics/summary`
Returns high-level aggregate risk metrics across all 27 Borno State LGAs for a given month. Ideal for top-level dashboard KPI cards.

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `month` | `integer` | No | `8` | Month of year (1 to 12) |

#### Example Request
```http
GET /api/v1/analytics/summary?month=8
```

#### Response Payload — Status `200 OK`
```json
{
  "total_lgas": 27,
  "high_risk_count": 8,
  "moderate_risk_count": 12,
  "low_risk_count": 7,
  "average_risk_probability": 0.584,
  "most_at_risk_lga": "Maiduguri",
  "data_source": "Borno State Outbreak Risk Model v1.0.0"
}
```

---

### `GET /api/v1/analytics/trends`
Returns a 12-month historical or projected risk trend for a specific location. Perfect for rendering line charts or time-series risk graphs.

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `location` | `string` | No | `"Maiduguri"` | LGA name to generate monthly trend data for |

#### Example Request
```http
GET /api/v1/analytics/trends?location=Maiduguri
```

#### Response Payload — Status `200 OK`
```json
{
  "location": "Maiduguri",
  "trend": [
    { "month": 1, "month_name": "January", "risk_probability": 0.15, "risk_level": "low" },
    { "month": 2, "month_name": "February", "risk_probability": 0.18, "risk_level": "low" },
    { "month": 3, "month_name": "March", "risk_probability": 0.22, "risk_level": "low" },
    { "month": 4, "month_name": "April", "risk_probability": 0.28, "risk_level": "low" },
    { "month": 5, "month_name": "May", "risk_probability": 0.35, "risk_level": "low" },
    { "month": 6, "month_name": "June", "risk_probability": 0.52, "risk_level": "moderate" },
    { "month": 7, "month_name": "July", "risk_probability": 0.68, "risk_level": "high" },
    { "month": 8, "month_name": "August", "risk_probability": 0.74, "risk_level": "high" },
    { "month": 9, "month_name": "September", "risk_probability": 0.71, "risk_level": "high" },
    { "month": 10, "month_name": "October", "risk_probability": 0.55, "risk_level": "moderate" },
    { "month": 11, "month_name": "November", "risk_probability": 0.30, "risk_level": "low" },
    { "month": 12, "month_name": "December", "risk_probability": 0.19, "risk_level": "low" }
  ]
}
```

---

### `GET /api/v1/analytics/high-risk`
Retrieves all LGAs classified as `high` or `moderate` risk for a specific month. Suitable for alerts, urgent action lists, and map overlays.

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `month` | `integer` | No | `8` | Month of year (1 to 12) |

#### Example Request
```http
GET /api/v1/analytics/high-risk?month=8
```

#### Response Payload — Status `200 OK`
```json
{
  "count": 2,
  "lgas": [
    {
      "location": "Maiduguri",
      "probability": 0.742,
      "risk_level": "high",
      "key_factors": ["High rainfall", "WASH deficit", "IDP population density"]
    },
    {
      "location": "Bama",
      "probability": 0.695,
      "risk_level": "high",
      "key_factors": ["WASH deficit", "IDP camp present"]
    }
  ]
}
```

---

### `GET /api/v1/analytics/lgas`
Returns the complete list of all 27 Local Government Areas in Borno State. Use this to populate frontend select dropdowns and search inputs.

#### Example Request
```http
GET /api/v1/analytics/lgas
```

#### Response Payload — Status `200 OK`
```json
{
  "count": 27,
  "lgas": [
    "Abadam", "Askira/Uba", "Bama", "Bayo", "Biu", "Chibok", "Damboa",
    "Dikwa", "Gubio", "Guzamala", "Gwoza", "Hawul", "Jere", "Kaga",
    "Kala/Balge", "Konduga", "Kukawa", "Kwaya Kusar", "Mafa", "Magumeri",
    "Maiduguri", "Marte", "Mobbar", "Monguno", "Ngala", "Nganzai", "Shani"
  ]
}
```

---

## 4. Authentication API

### `POST /api/v1/auth/register`
Registers a new user account.

#### Request Body
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "password": "SecurePassword123!"
}
```

#### Response Payload — Status `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2026-07-22T12:00:00Z"
}
```

---

### `POST /api/v1/auth/login`
Authenticates user credentials and returns a JWT bearer access token.

#### Request Body
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

#### Response Payload — Status `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### `GET /api/v1/auth/me`
Retrieves the profile of the currently logged-in user.

#### Request Headers
```http
Authorization: Bearer <access_token>
```

#### Response Payload — Status `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2026-07-22T12:00:00Z"
}
```

---

### `POST /api/v1/auth/logout`
Invalidates the current JWT access token.

#### Request Headers
```http
Authorization: Bearer <access_token>
```

#### Response Payload — Status `200 OK`
```json
{
  "message": "Successfully logged out."
}
```

---

### `POST /api/v1/auth/forgot-password`
Submits email to request a password reset token.

#### Request Body
```json
{
  "email": "user@example.com"
}
```

#### Response Payload — Status `200 OK`
```json
{
  "message": "Password reset token generated. Use it with /reset-password.",
  "reset_token": "reset_token_xyz123"
}
```

---

### `POST /api/v1/auth/reset-password`
Resets user password using the token issued by `/forgot-password`.

#### Request Body
```json
{
  "token": "reset_token_xyz123",
  "new_password": "NewSecurePassword456!"
}
```

#### Response Payload — Status `200 OK`
```json
{
  "message": "Password has been reset successfully. You can now log in."
}
```

---

### `POST /api/v1/auth/change-password`
Changes account password for an authenticated user.

#### Request Headers
```http
Authorization: Bearer <access_token>
```

#### Request Body
```json
{
  "current_password": "SecurePassword123!",
  "new_password": "NewSecurePassword456!"
}
```

#### Response Payload — Status `200 OK`
```json
{
  "message": "Password updated successfully."
}
```

---

## 5. System Health & Metadata API

### `GET /health`
Returns system status, API version, and ML model status.

#### Example Request
```http
GET /health
```

#### Response Payload — Status `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_status": "loaded"
}
```

---

### `GET /api/v1/datasets`
Lists metadata for underlying ML trained models and preprocessor pipeline artifacts.

#### Example Request
```http
GET /api/v1/datasets
```

#### Response Payload — Status `200 OK`
```json
{
  "datasets": [
    {
      "name": "Cholera Model",
      "path": "c:\\Users\\...\\models\\cholera_pipeline.joblib",
      "exists": true,
      "size_bytes": 524288
    },
    {
      "name": "Preprocessor Pipeline",
      "path": "c:\\Users\\...\\models\\preprocessor.joblib",
      "exists": true,
      "size_bytes": 131072
    }
  ]
}
```

---

## 6. TypeScript Interface Definitions for Frontend

Copy and paste these TypeScript interfaces directly into your frontend application (`src/types/api.ts`):

```typescript
// --- Request Types ---

export interface PredictionRequest {
  location: string;
  rainfall: number;
  population: number;
  population_density: number;
  wash_score: number;
  month: number;
  idp_camp?: boolean;
  conflict_score?: number; // OPTIONAL: May be omitted by frontend
}

export interface RegisterRequest {
  email: string;
  username: string;
  full_name: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

// --- Response Types ---

export interface ContributingFactor {
  factor: string;
  value: number;
  impact: 'high' | 'moderate' | 'low';
}

export interface PredictionResponse {
  location: string;
  risk_level: 'high' | 'moderate' | 'low';
  probability: number;
  confidence: number;
  model_version: string;
  prediction_method: 'rule-based' | 'ml-model';
  contributing_factors: ContributingFactor[];
  explanation: string;
}

export interface AnalyticsSummary {
  total_lgas: number;
  high_risk_count: number;
  moderate_risk_count: number;
  low_risk_count: number;
  average_risk_probability: number;
  most_at_risk_lga: string;
  data_source: string;
}

export interface TrendDataPoint {
  month: number;
  month_name: string;
  risk_probability: number;
  risk_level: 'high' | 'moderate' | 'low';
}

export interface TrendResponse {
  location: string;
  trend: TrendDataPoint[];
}

export interface HighRiskLGA {
  location: string;
  probability: number;
  risk_level: 'high' | 'moderate' | 'low';
  key_factors: string[];
}

export interface HighRiskResponse {
  count: number;
  lgas: HighRiskLGA[];
}

export interface LGAListResponse {
  count: number;
  lgas: string[];
}

export interface UserResponse {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface AuthMessageResponse {
  message: string;
}

export interface ForgotPasswordResponse {
  message: string;
  reset_token: string | null;
}

export interface ErrorResponse {
  error: string;
  message: string;
}
```

---

## 7. HTTP Status Codes & Error Handling

| Status Code | Meaning | Cause / Action |
|---|---|---|
| `200 OK` | Success | Request succeeded. Returns data payload. |
| `201 Created` | Created | User account created successfully. |
| `400 Bad Request` | Bad Request | Invalid request parameters (e.g., incorrect password during password change). |
| `401 Unauthorized` | Unauthorized | Missing or invalid JWT access token in `Authorization` header. |
| `403 Forbidden` | Forbidden | Account disabled or insufficient privileges. |
| `404 Not Found` | Resource Not Found | Endpoint or requested record does not exist. |
| `422 Unprocessable Entity` | Validation Error | Request body failed Pydantic validation rules (e.g., `wash_score` out of range `0..1`). Returns list of specific field validation failures. |
| `500 Internal Server Error` | Server Error | Internal server exception. Check server logs. |

### Validation Error Response Example (HTTP 422)
```json
{
  "detail": [
    {
      "loc": ["body", "wash_score"],
      "msg": "Input should be less than or equal to 1",
      "type": "less_than_equal"
    }
  ]
}
```

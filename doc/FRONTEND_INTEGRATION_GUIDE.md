# Cholera Outbreak Prediction System — Frontend Integration Guide

This guide provides practical code examples for frontend developers integrating with the Cholera Outbreak Prediction API.

---

## 1. Quick Start API Client (`apiClient.ts`)

Create a unified API service module in your frontend project:

```typescript
import {
  PredictionRequest,
  PredictionResponse,
  AnalyticsSummary,
  TrendResponse,
  HighRiskResponse,
  LGAListResponse,
  LoginRequest,
  TokenResponse,
  UserResponse,
} from './types/api';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

class ApiClient {
  private token: string | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  public setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || errorData.detail || `HTTP Error ${response.status}`);
    }

    return response.json();
  }

  // --- Auth Endpoints ---

  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const data = await this.request<TokenResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    this.setToken(data.access_token);
    return data;
  }

  async getProfile(): Promise<UserResponse> {
    return this.request<UserResponse>('/api/v1/auth/me');
  }

  async logout(): Promise<void> {
    await this.request('/api/v1/auth/logout', { method: 'POST' });
    this.setToken(null);
  }

  // --- Prediction Endpoint ---

  /**
   * Submit environmental & demographic features to compute outbreak risk.
   * Note: `conflict_score` is optional and does not need to be passed in payload.
   */
  async predictRisk(payload: PredictionRequest): Promise<PredictionResponse> {
    return this.request<PredictionResponse>('/api/v1/predict', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // --- Dashboard & Analytics Endpoints ---

  async getSummary(month: number = 8): Promise<AnalyticsSummary> {
    return this.request<AnalyticsSummary>(`/api/v1/analytics/summary?month=${month}`);
  }

  async getTrends(location: string = 'Maiduguri'): Promise<TrendResponse> {
    return this.request<TrendResponse>(`/api/v1/analytics/trends?location=${encodeURIComponent(location)}`);
  }

  async getHighRiskLGAs(month: number = 8): Promise<HighRiskResponse> {
    return this.request<HighRiskResponse>(`/api/v1/analytics/high-risk?month=${month}`);
  }

  async getLGAs(): Promise<LGAListResponse> {
    return this.request<LGAListResponse>('/api/v1/analytics/lgas');
  }
}

export const api = new ApiClient();
```

---

## 2. React Form Integration Example

```tsx
import React, { useState } from 'react';
import { api } from './apiClient';
import { PredictionResponse } from './types/api';

export const RiskPredictorForm: React.FC = () => {
  const [location, setLocation] = useState('Maiduguri');
  const [rainfall, setRainfall] = useState(125);
  const [population, setPopulation] = useState(150000);
  const [density, setDensity] = useState(5000);
  const [washScore, setWashScore] = useState(0.2);
  const [idpCamp, setIdpCamp] = useState(true);
  const [month, setMonth] = useState(8);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // NOTE: conflict_score is NOT sent here because it's optional
      const response = await api.predictRisk({
        location,
        rainfall: Number(rainfall),
        population: Number(population),
        population_density: Number(density),
        wash_score: Number(washScore),
        idp_camp: idpCamp,
        month: Number(month),
      });

      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Failed to generate prediction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 20 }}>
      <h2>Cholera Risk Prediction</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label>LGA Location:</label>
          <input value={location} onChange={(e) => setLocation(e.target.value)} required />
        </div>

        <div>
          <label>Rainfall (mm):</label>
          <input type="number" value={rainfall} onChange={(e) => setRainfall(Number(e.target.value))} required />
        </div>

        <div>
          <label>Population:</label>
          <input type="number" value={population} onChange={(e) => setPopulation(Number(e.target.value))} required />
        </div>

        <div>
          <label>Population Density (people/km²):</label>
          <input type="number" value={density} onChange={(e) => setDensity(Number(e.target.value))} required />
        </div>

        <div>
          <label>WASH Score (0.0 = Poor, 1.0 = Excellent):</label>
          <input type="number" step="0.05" min="0" max="1" value={washScore} onChange={(e) => setWashScore(Number(e.target.value))} required />
        </div>

        <div>
          <label>
            <input type="checkbox" checked={idpCamp} onChange={(e) => setIdpCamp(e.target.checked)} />
            IDP Camp Present
          </label>
        </div>

        <div>
          <label>Month (1-12):</label>
          <input type="number" min="1" max="12" value={month} onChange={(e) => setMonth(Number(e.target.value))} required />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Predict Risk'}
        </button>
      </form>

      {error && <div style={{ color: 'red', marginTop: 10 }}>Error: {error}</div>}

      {result && (
        <div style={{ marginTop: 20, padding: 15, border: '1px solid #ccc', borderRadius: 8 }}>
          <h3>Risk Assessment for {result.location}</h3>
          <p>
            <strong>Risk Level:</strong>{' '}
            <span style={{ color: result.risk_level === 'high' ? 'red' : result.risk_level === 'moderate' ? 'orange' : 'green' }}>
              {result.risk_level.toUpperCase()}
            </span>
          </p>
          <p><strong>Probability:</strong> {(result.probability * 100).toFixed(1)}%</p>
          <p><strong>Explanation:</strong> {result.explanation}</p>

          <h4>Contributing Factors</h4>
          <ul>
            {result.contributing_factors.map((f, i) => (
              <li key={i}>
                {f.factor} — Impact: <strong>{f.impact}</strong>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
```

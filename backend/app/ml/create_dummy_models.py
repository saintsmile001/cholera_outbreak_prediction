"""Create lightweight dummy ML artifacts for local testing.

These files are intentionally simple and can be replaced later with a real
trained model and a real preprocessing pipeline.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def build_dummy_training_data() -> tuple[np.ndarray, np.ndarray]:
    """Generate a small synthetic feature/label dataset."""
    X = np.array(
        [
            [0.20, 0.10, 0.10, 0.15, 0.10, 0.0, 0.0],
            [0.45, 0.35, 0.40, 0.35, 0.25, 1.0, 0.0],
            [0.65, 0.60, 0.65, 0.60, 0.45, 1.0, 1.0],
            [0.85, 0.80, 0.90, 0.80, 0.70, 1.0, 1.0],
            [0.10, 0.05, 0.05, 0.10, 0.05, 0.0, 0.0],
            [0.33, 0.22, 0.25, 0.30, 0.18, 0.0, 1.0],
            [0.75, 0.70, 0.80, 0.70, 0.65, 1.0, 1.0],
            [0.55, 0.50, 0.55, 0.50, 0.40, 1.0, 0.0],
        ],
        dtype=float,
    )
    y = np.array([0, 0, 1, 1, 0, 0, 1, 1], dtype=int)
    return X, y


def main() -> None:
    """Train and save the dummy preprocessor and model artifacts."""
    backend_dir = Path(__file__).resolve().parent.parent.parent
    models_dir = backend_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    X, y = build_dummy_training_data()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(random_state=42, max_iter=500)
    model.fit(X_scaled, y)

    preprocessor_path = models_dir / "preprocessor.joblib"
    model_path = models_dir / "cholera_model.joblib"

    joblib.dump(scaler, preprocessor_path)
    joblib.dump(model, model_path)

    print(f"Saved preprocessor to {preprocessor_path}")
    print(f"Saved model to {model_path}")


if __name__ == "__main__":
    main()

import csv
import io
from collections import defaultdict
from pathlib import Path

from app.core.exceptions import DatasetError, InvalidInputError
from app.core.logger import logger
from app.ml.predictor import generate_prediction
from app.models.request_models import PredictionRequest
from app.models.response_models import (
    DatasetPredictionResponse,
    DatasetRecordPrediction,
    LGADatasetSummary,
    PredictionResponse,
)


def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Run a cholera outbreak risk prediction.

    This service-level function is the single entry point for
    all prediction logic.  Additional business rules (rate-limiting,
    audit logging, caching, etc.) can be added here without
    touching the route or the ML layer.
    """
    logger.info(
        "Prediction requested — location=%s, month=%d, rainfall=%.1f, idp_camp=%s",
        request.location,
        request.month,
        request.rainfall,
        request.idp_camp,
    )

    response = generate_prediction(request)

    logger.info(
        "Prediction complete — location=%s, risk=%s, prob=%.3f, method=%s",
        response.location,
        response.risk_level,
        response.probability,
        response.prediction_method,
    )

    return response


def _safe_float(val: object, default: float = 0.0) -> float:
    try:
        return float(val) if val is not None and str(val).strip() != "" else default
    except (ValueError, TypeError):
        return default


def _safe_int(val: object, default: int = 0) -> int:
    try:
        return int(float(val)) if val is not None and str(val).strip() != "" else default
    except (ValueError, TypeError):
        return default


def _safe_bool(val: object) -> bool:
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    return s in ("true", "1", "yes", "t")


def predict_from_dataset(
    file_content: bytes | None = None,
    file_name: str | None = None,
    location_filter: str | None = None,
    month_filter: int | None = None,
    year_filter: int | None = None,
    limit: int = 200,
) -> DatasetPredictionResponse:
    """
    Generate predictions from a dataset (uploaded CSV bytes or default local CSV).
    Groups and returns prediction data based on local government areas (LGAs) present in the dataset.
    """
    if file_content is not None:
        try:
            text = file_content.decode("utf-8-sig", errors="replace")
        except Exception as exc:
            raise InvalidInputError(f"Could not decode CSV file content: {exc}")
        source_name = file_name or "Uploaded Dataset"
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
    else:
        candidates = [
            Path("Borno_Cholera_Hackathon_2017_2026.csv"),
            Path("backend/realdata/cholere_dataset.csv"),
            Path("backend/Borno_Cholera_Hackathon_2017_2026.csv"),
        ]
        file_path = next((p for p in candidates if p.exists()), None)
        if not file_path:
            raise DatasetError("No default dataset CSV file found on server.")

        source_name = file_path.name
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    if not rows:
        raise InvalidInputError("Dataset is empty or contains no readable rows.")

    logger.info(
        "Processing dataset prediction for source=%s (total rows=%d, location_filter=%s)",
        source_name,
        len(rows),
        location_filter,
    )

    all_record_preds: list[DatasetRecordPrediction] = []
    by_lga: dict[str, list[DatasetRecordPrediction]] = defaultdict(list)

    for row in rows:
        lga = (
            row.get("LGA")
            or row.get("lga")
            or row.get("Location")
            or row.get("location")
            or "Unknown"
        ).strip()

        if location_filter and lga.lower() != location_filter.strip().lower():
            continue

        year = _safe_int(row.get("Year") or row.get("year")) or None
        week = _safe_int(row.get("Week") or row.get("week")) or None
        month = _safe_int(row.get("Month") or row.get("month"), default=8)
        if month < 1 or month > 12:
            month = 8

        if month_filter and month != month_filter:
            continue
        if year_filter and year is not None and year != year_filter:
            continue

        rainfall = _safe_float(row.get("Rainfall_mm") or row.get("rainfall"))
        pop_density = _safe_float(row.get("Population_Density") or row.get("population_density"), default=1000.0)

        if "Safe_Water_pct" in row:
            wash_score = round(_safe_float(row.get("Safe_Water_pct"), 50.0) / 100.0, 3)
        elif "wash_score" in row:
            wash_score = _safe_float(row.get("wash_score"), 0.5)
        else:
            wash_score = 0.5
        wash_score = max(0.0, min(1.0, wash_score))

        idp_pop = _safe_float(row.get("IDP_Population") or row.get("idp_population"), 0.0)
        if "idp_camp" in row:
            idp_camp = _safe_bool(row.get("idp_camp"))
        else:
            idp_camp = idp_pop > 5000.0

        conflict_score = _safe_float(row.get("Conflict_Score") or row.get("conflict_score"), 0.0)
        conflict_score = max(0.0, min(1.0, conflict_score))

        population = _safe_int(row.get("Population") or row.get("population"), default=150000)

        req = PredictionRequest(
            location=lga,
            rainfall=rainfall,
            population=population,
            population_density=pop_density,
            wash_score=wash_score,
            conflict_score=conflict_score,
            idp_camp=idp_camp,
            month=month,
        )

        pred: PredictionResponse = generate_prediction(req)

        rec_pred = DatasetRecordPrediction(
            year=year,
            week=week,
            month=month,
            location=lga,
            rainfall=rainfall,
            population_density=pop_density,
            wash_score=wash_score,
            risk_level=pred.risk_level,
            probability=pred.probability,
            confidence=pred.confidence,
            prediction_method=pred.prediction_method,
            contributing_factors=pred.contributing_factors,
            explanation=pred.explanation,
        )

        all_record_preds.append(rec_pred)
        by_lga[lga].append(rec_pred)

        if len(all_record_preds) >= limit:
            break

    lgas_present = sorted(list(by_lga.keys()))
    summary_by_lga: list[LGADatasetSummary] = []

    for lga_name in lgas_present:
        preds = by_lga[lga_name]
        avg_prob = round(sum(p.probability for p in preds) / len(preds), 3) if preds else 0.0
        max_prob = max((p.probability for p in preds), default=0.0)
        risk_levels = [p.risk_level for p in preds]
        highest_risk = (
            "high"
            if "high" in risk_levels
            else "moderate"
            if "moderate" in risk_levels
            else "low"
        )

        summary_by_lga.append(
            LGADatasetSummary(
                location=lga_name,
                total_records=len(preds),
                average_probability=avg_prob,
                max_probability=max_prob,
                highest_risk_level=highest_risk,
                predictions=preds,
            )
        )

    return DatasetPredictionResponse(
        dataset_name=source_name,
        total_records_processed=len(all_record_preds),
        lgas_present=lgas_present,
        summary_by_lga=summary_by_lga,
        all_predictions=all_record_preds,
    )


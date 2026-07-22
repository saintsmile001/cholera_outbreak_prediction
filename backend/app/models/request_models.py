"""
Pydantic request models for API validation.

Every incoming API request body is validated against these schemas.
Invalid data is automatically rejected with a 422 response.
"""

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Schema for a cholera outbreak risk prediction request."""

    location: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the LGA or location in Borno State.",
        examples=["Maiduguri"],
    )
    rainfall: float = Field(
        ...,
        ge=0,
        le=1000,
        description="Rainfall in millimetres over the reference period.",
        examples=[125.0],
    )
    population: int = Field(
        ...,
        ge=0,
        le=10_000_000,
        description="Total population of the LGA.",
        examples=[150000],
    )
    population_density: float = Field(
        ...,
        ge=0,
        le=100_000,
        description="Population density (people per km²).",
        examples=[5000.0],
    )
    wash_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="WASH (Water, Sanitation & Hygiene) score from 0 (worst) to 1 (best).",
        examples=[0.2],
    )
    conflict_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Conflict/insurgency intensity from 0 (peaceful) to 1 (severe).",
        examples=[0.8],
    )
    idp_camp: bool = Field(
        default=False,
        description="Whether an IDP (Internally Displaced Persons) camp is present.",
        examples=[True],
    )
    month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Month of the year (1 = January, 12 = December).",
        examples=[8],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "location": "Maiduguri",
                    "rainfall": 125.0,
                    "population": 150000,
                    "population_density": 5000.0,
                    "wash_score": 0.2,
                    "conflict_score": 0.8,
                    "idp_camp": True,
                    "month": 8,
                }
            ]
        }
    }

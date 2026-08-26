from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    """
    Request payload for customer churn prediction.
    """

    model_config = ConfigDict(extra="forbid")

    age: int = Field(
        ...,
        ge=18,
        le=100,
        description="Customer age",
    )

    tenure_months: int = Field(
        ...,
        ge=0,
        le=120,
        description="Customer tenure in months",
    )

    monthly_spend: float = Field(
        ...,
        gt=0,
        description="Customer monthly spending",
    )

    support_tickets: int = Field(
        ...,
        ge=0,
        le=100,
        description="Number of customer support tickets",
    )

    contract_type: Literal[
        "monthly",
        "yearly",
    ] = Field(
        ...,
        description="Customer contract type",
    )


class PredictionResponse(BaseModel):
    """
    Prediction response returned by the API.
    """

    prediction: int = Field(
        ...,
        description="Predicted churn class: 0 or 1",
    )

    churn_probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probability that the customer will churn",
    )

    model_name: str = Field(
        ...,
        description="Model registry name",
    )

    model_version: str = Field(
        ...,
        description="Model version used for prediction",
    )

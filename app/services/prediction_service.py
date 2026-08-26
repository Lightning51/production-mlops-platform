import pandas as pd

from app.config.settings import get_settings
from app.model.model_loader import model_loader
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)


class PredictionService:
    """
    Business/service layer responsible for ML inference.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    def predict(
        self,
        request: PredictionRequest,
    ) -> PredictionResponse:
        """
        Generate a churn prediction for the supplied customer data.
        """

        model = model_loader.get_model()

        input_data = pd.DataFrame(
            [
                {
                    "age": request.age,
                    "tenure_months": request.tenure_months,
                    "monthly_spend": request.monthly_spend,
                    "support_tickets": request.support_tickets,
                    "contract_type": request.contract_type,
                }
            ]
        )

        prediction = int(model.predict(input_data)[0])

        probabilities = model.predict_proba(input_data)[0]

        churn_probability = float(probabilities[1])

        return PredictionResponse(
            prediction=prediction,
            churn_probability=round(
                churn_probability,
                6,
            ),
            model_name=self._settings.model_name,
            model_version=self._settings.model_version,
        )


prediction_service = PredictionService()

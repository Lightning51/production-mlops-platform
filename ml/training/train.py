from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import mlflow
import mlflow.sklearn
from mlflow import MlflowClient
from mlflow.models import infer_signature

# =============================================================================
# Configuration
# =============================================================================

DATA_PATH = Path("ml/data/customer_churn.csv")

MODEL_DIR = Path("ml/models")
MODEL_PATH = MODEL_DIR / "customer_churn_model.joblib"

TARGET_COLUMN = "churn"

TEST_SIZE = 0.20
RANDOM_STATE = 42
MAX_ITER = 1000

MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
MLFLOW_EXPERIMENT_NAME = "customer-churn"

REGISTERED_MODEL_NAME = "customer-churn-model"

MINIMUM_ROC_AUC = 0.80


NUMERIC_FEATURES = [
    "age",
    "tenure_months",
    "monthly_spend",
    "support_tickets",
]

CATEGORICAL_FEATURES = [
    "contract_type",
]


# =============================================================================
# Data Loading
# =============================================================================


def load_data() -> pd.DataFrame:
    """
    Load the training dataset from disk.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    data = pd.read_csv(DATA_PATH)

    if data.empty:
        raise ValueError("Dataset is empty.")

    required_columns = {
        *NUMERIC_FEATURES,
        *CATEGORICAL_FEATURES,
        TARGET_COLUMN,
    }

    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing_columns)}")

    return data


# =============================================================================
# Model Pipeline
# =============================================================================


def build_pipeline() -> Pipeline:
    """
    Build the complete preprocessing + ML model pipeline.
    """

    numeric_transformer = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_transformer,
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                categorical_transformer,
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    model = LogisticRegression(
        max_iter=MAX_ITER,
        random_state=RANDOM_STATE,
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )

    return pipeline


# =============================================================================
# Model Evaluation
# =============================================================================


def evaluate_model(
    pipeline: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict[str, float]:
    """
    Evaluate the trained model and return metrics.
    """

    predictions = pipeline.predict(X_test)

    probabilities = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(
            y_test,
            predictions,
        ),
        "roc_auc": roc_auc_score(
            y_test,
            probabilities,
        ),
        "precision": precision_score(
            y_test,
            predictions,
        ),
        "recall": recall_score(
            y_test,
            predictions,
        ),
        "f1_score": f1_score(
            y_test,
            predictions,
        ),
    }

    print("\nModel Evaluation")
    print("================")

    print(f"Accuracy : {metrics['accuracy']:.4f}")

    print(f"ROC-AUC  : {metrics['roc_auc']:.4f}")

    print(f"Precision: {metrics['precision']:.4f}")

    print(f"Recall   : {metrics['recall']:.4f}")

    print(f"F1 Score : {metrics['f1_score']:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
        )
    )

    return metrics


# =============================================================================
# Model Quality Gate
# =============================================================================


def validate_model_quality(
    roc_auc: float,
) -> None:
    """
    Fail the pipeline if the model does not meet
    the minimum quality threshold.
    """

    print(f"\nModel Quality Gate: ROC-AUC {roc_auc:.4f} (minimum required: {MINIMUM_ROC_AUC:.4f})")

    if roc_auc < MINIMUM_ROC_AUC:
        raise RuntimeError(
            f"Model quality gate failed. ROC-AUC={roc_auc:.4f}, required={MINIMUM_ROC_AUC:.4f}"
        )

    print("Model quality gate PASSED.")


# =============================================================================
# Save Local Model
# =============================================================================


def save_local_model(
    pipeline: Pipeline,
) -> None:
    """
    Save the trained pipeline locally.
    """

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        pipeline,
        MODEL_PATH,
    )

    print(f"\nModel saved to: {MODEL_PATH}")


# =============================================================================
# MLflow Model Registration
# =============================================================================


def register_model(
    model_info,
    run_id: str,
) -> None:
    """
    Register the MLflow model in the Model Registry.
    """

    client = MlflowClient()

    try:
        client.get_registered_model(REGISTERED_MODEL_NAME)

        print(f"Registered model already exists: {REGISTERED_MODEL_NAME}")

    except Exception:
        client.create_registered_model(REGISTERED_MODEL_NAME)

        print(f"Created registered model: {REGISTERED_MODEL_NAME}")

    model_version = client.create_model_version(
        name=REGISTERED_MODEL_NAME,
        source=model_info.model_uri,
        run_id=run_id,
    )

    print(f"Registered model version: {model_version.version}")


# =============================================================================
# Main Training Pipeline
# =============================================================================


def main() -> None:
    # -------------------------------------------------------------------------
    # Configure MLflow
    # -------------------------------------------------------------------------

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    # -------------------------------------------------------------------------
    # Load dataset
    # -------------------------------------------------------------------------

    print("Loading dataset...")

    data = load_data()

    X = data.drop(columns=[TARGET_COLUMN])

    y = data[TARGET_COLUMN]

    # -------------------------------------------------------------------------
    # Train/Test Split
    # -------------------------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    print(f"Training samples: {len(X_train)}")

    print(f"Testing samples:  {len(X_test)}")

    # -------------------------------------------------------------------------
    # Start MLflow Run
    # -------------------------------------------------------------------------

    with mlflow.start_run() as run:
        # ---------------------------------------------------------------------
        # MLflow Tags
        # ---------------------------------------------------------------------

        mlflow.set_tag(
            "model_type",
            "logistic_regression",
        )

        mlflow.set_tag(
            "dataset",
            "customer_churn",
        )

        mlflow.set_tag(
            "environment",
            "development",
        )

        # ---------------------------------------------------------------------
        # MLflow Parameters
        # ---------------------------------------------------------------------

        mlflow.log_params(
            {
                "algorithm": "LogisticRegression",
                "test_size": TEST_SIZE,
                "random_state": RANDOM_STATE,
                "max_iter": MAX_ITER,
                "numeric_features": ",".join(NUMERIC_FEATURES),
                "categorical_features": ",".join(CATEGORICAL_FEATURES),
            }
        )

        # ---------------------------------------------------------------------
        # Train
        # ---------------------------------------------------------------------

        print("\nTraining model...")

        pipeline = build_pipeline()

        pipeline.fit(
            X_train,
            y_train,
        )

        # ---------------------------------------------------------------------
        # Evaluate
        # ---------------------------------------------------------------------

        print("\nEvaluating model...")

        metrics = evaluate_model(
            pipeline,
            X_test,
            y_test,
        )

        # ---------------------------------------------------------------------
        # Log Metrics
        # ---------------------------------------------------------------------

        mlflow.log_metrics(metrics)

        # ---------------------------------------------------------------------
        # Quality Gate
        # ---------------------------------------------------------------------

        roc_auc = metrics["roc_auc"]

        try:
            validate_model_quality(roc_auc)

            mlflow.set_tag(
                "quality_gate",
                "PASSED",
            )

        except RuntimeError:
            mlflow.set_tag(
                "quality_gate",
                "FAILED",
            )

            raise

        # ---------------------------------------------------------------------
        # Save Local Model
        # ---------------------------------------------------------------------

        save_local_model(pipeline)

        # ---------------------------------------------------------------------
        # MLflow Model Signature
        # ---------------------------------------------------------------------

        signature = infer_signature(
            X_train,
            pipeline.predict(X_train),
        )

        # ---------------------------------------------------------------------
        # Log Model to MLflow
        # ---------------------------------------------------------------------

        model_info = mlflow.sklearn.log_model(
            sk_model=pipeline,
            name="customer_churn_model",
            signature=signature,
            input_example=X_test.head(1),
        )

        print(f"MLflow Model URI: {model_info.model_uri}")

        # ---------------------------------------------------------------------
        # Register Model
        # ---------------------------------------------------------------------

        register_model(
            model_info=model_info,
            run_id=run.info.run_id,
        )

        # ---------------------------------------------------------------------
        # Run Information
        # ---------------------------------------------------------------------

        print(f"\nMLflow Run ID: {run.info.run_id}")


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    main()

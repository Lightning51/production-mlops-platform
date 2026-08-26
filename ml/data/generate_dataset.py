from pathlib import Path

import numpy as np
import pandas as pd

RANDOM_SEED = 42
DATASET_SIZE = 5000


def sigmoid(value: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-value))


def generate_dataset() -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)

    age = rng.integers(18, 70, DATASET_SIZE)
    tenure_months = rng.integers(1, 72, DATASET_SIZE)
    monthly_spend = rng.uniform(500, 10000, DATASET_SIZE).round(2)
    support_tickets = rng.integers(0, 10, DATASET_SIZE)

    contract_type = rng.choice(
        ["monthly", "yearly"],
        DATASET_SIZE,
        p=[0.65, 0.35],
    )

    monthly_contract = (contract_type == "monthly").astype(float)

    # Business-driven churn signal.
    score = (
        2.0 * monthly_contract
        + 0.45 * support_tickets
        - 0.045 * tenure_months
        + 0.00004 * monthly_spend
        - 0.01 * age
        + rng.normal(0, 0.15, DATASET_SIZE)
    )

    probability = sigmoid(score - 1.0)

    churn = rng.binomial(1, probability)

    return pd.DataFrame(
        {
            "age": age,
            "tenure_months": tenure_months,
            "monthly_spend": monthly_spend,
            "support_tickets": support_tickets,
            "contract_type": contract_type,
            "churn": churn,
        }
    )


def main() -> None:
    output_directory = Path("ml/data")
    output_directory.mkdir(parents=True, exist_ok=True)

    output_file = output_directory / "customer_churn.csv"

    dataset = generate_dataset()

    dataset.to_csv(output_file, index=False)

    print(f"Dataset generated: {output_file}")
    print(f"Rows: {len(dataset)}")
    print(f"Columns: {len(dataset.columns)}")
    print(f"Churn rate: {dataset['churn'].mean():.2%}")


if __name__ == "__main__":
    main()

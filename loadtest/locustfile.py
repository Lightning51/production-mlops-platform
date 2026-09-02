from locust import HttpUser, between, task


class PredictionUser(HttpUser):
    wait_time = between(0.1, 0.3)

    @task
    def predict(self):
        self.client.post(
            "/api/v1/predict",
            json={
                "age": 35,
                "tenure_months": 24,
                "monthly_spend": 75.50,
                "support_tickets": 2,
                "contract_type": "monthly",
            },
        )

from locust import HttpUser, task, between
import json, random

# Leave BASE_URL empty and provide it in the UI to avoid hardcoding
BASE_URL = "https://bumhz6jxa3.execute-api.us-east-1.amazonaws.com"

SAMPLES = [
    "Ciao, come stai oggi a Roma?",
    "Tim Cook met Elon Musk in Rome on Monday.",
    "Amazon acquired Whole Foods for $13.7 billion in 2017.",
    "The conference will be held at Stanford University in California.",
    "Barack Obama visited Berlin in 2013."
]

class NerUser(HttpUser):
    wait_time = between(0.2, 1.0)
    if BASE_URL:
        host = BASE_URL  # otherwise you’ll fill Host in the UI

    @task
    def ner(self):
        payload = {"text": random.choice(SAMPLES)}
        self.client.post(
            "/ner",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )

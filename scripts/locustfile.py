"""Locust load-test script for the RAG API.

Set the target and credential in the environment. Do not hardcode either.

    $env:RAG_API_KEY = "<your key>"
    locust -f scripts/locustfile.py --headless -u 1 -r 1 -t 10m --host http://localhost:8000

A key that was previously committed must be rotated. Deleting it from this file
does not remove it from Git history and does not revoke it.
"""

import os
import random

from locust import HttpUser, between, task

RAG_API_KEY = os.environ.get("RAG_API_KEY", "").strip()
if not RAG_API_KEY:
    raise RuntimeError(
        "RAG_API_KEY is required for load testing. Export it in the environment before "
        "starting Locust. Do not commit the value."
    )

SAMPLE_QUESTIONS = [
    "What is a Kubernetes pod?",
    "Explain the difference between a process and a thread.",
    "What is a REST API and how does it work?",
    "How does a database index improve query performance?",
    "What is the purpose of a load balancer in a web application?",
]


class RAGQueryUser(HttpUser):
    """Simulates a user asking questions to the RAG /query endpoint."""

    wait_time = between(1, 5)

    @task
    def query(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {RAG_API_KEY}",
        }
        question = random.choice(SAMPLE_QUESTIONS)
        payload = {
            "q": question,
            "thread_id": f"locust-{random.randint(1, 1000000)}",
        }
        with self.client.post(
            "/query",
            json=payload,
            headers=headers,
            catch_response=True,
            name="/query",
            timeout=60,
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "error":
                        response.failure(f"API error: {data.get('message')}")
                    else:
                        response.success()
                except Exception as exc:
                    response.failure(f"Invalid JSON: {exc}")
            else:
                response.failure(f"HTTP {response.status_code}")

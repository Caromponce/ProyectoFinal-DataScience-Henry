import os
import requests

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def get_recommendations(user_id: int, product_ids: list[int] | None = None, n: int = 5):
    """
    Cliente real para consumir POST /recommend desde FastAPI.
    """

    payload = {
        "user_id": user_id,
        "product_ids": product_ids or [],
        "n": n
    }

    response = requests.post(
        f"{API_URL}/recommend",
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    return response.json()


def get_metrics():
    """
    Cliente real para consumir GET /metrics desde FastAPI.
    """

    response = requests.get(
        f"{API_URL}/metrics",
        timeout=30
    )

    response.raise_for_status()
    return response.json()


def get_user_segment(user_id: int):
    """
    Cliente real para consumir GET /segment/{user_id} desde FastAPI.
    """

    response = requests.get(
        f"{API_URL}/segment/{user_id}",
        timeout=30
    )

    response.raise_for_status()
    return response.json()


def get_market_basket():
    """
    Placeholder temporal.
    Las recomendaciones MBA se consumen desde /recommend según segmento.
    """

    return {
        "rules": []
    }
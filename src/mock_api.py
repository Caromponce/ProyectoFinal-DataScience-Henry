# importar librerías
import json
from pathlib import Path


# definir ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parents[1]


def get_mock_recommendations():
    """
    Simula la respuesta del endpoint:
    GET /recommend/{user_id}?n=5
    """

    file_path = BASE_DIR / "data" / "mock" / "recommendations.json"

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data

def get_mock_metrics():
    """
    Simula la respuesta del endpoint:
    GET /metrics
    """

    file_path = BASE_DIR / "data" / "mock" / "metrics.json"

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data

def get_mock_segments():
    """
    Simula la respuesta del endpoint:
    GET /segments
    """

    file_path = BASE_DIR / "data" / "mock" / "segments.json"

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data

def get_mock_market_basket():
    """
    Simula la respuesta del endpoint:
    GET /market-basket
    """

    file_path = BASE_DIR / "data" / "mock" / "market_basket.json"

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data
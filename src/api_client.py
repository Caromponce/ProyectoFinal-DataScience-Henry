# importar funciones mock
from src.mock_api import (
    get_mock_recommendations,
    get_mock_metrics,
    get_mock_segments,
    get_mock_market_basket
)


def get_recommendations(user_id: int, n: int = 5):
    """
    Función cliente que hoy usa datos mock.
    Más adelante se reemplaza por una llamada real a FastAPI.
    """

    data = get_mock_recommendations()

    # ajustamos user_id y cantidad de recomendaciones
    data["user_id"] = user_id
    data["recommendations"] = data["recommendations"][:n]

    return data

def get_metrics():
    """
    Función cliente que hoy usa datos mock.
    Más adelante consumirá GET /metrics desde FastAPI.
    """

    return get_mock_metrics()

def get_segments():
    """
    Cliente para la distribución de segmentos.
    Más adelante consumirá GET /segments.
    """

    return get_mock_segments()

def get_market_basket():
    """
    Cliente para reglas de asociación.
    Más adelante consumirá GET /market-basket.
    """

    return get_mock_market_basket()
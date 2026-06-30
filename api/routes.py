from fastapi import APIRouter

from api.services import (
    build_recommendation_response,
    build_user_segment_response,
    build_metrics_response,
    build_market_basket_response,
)

from api.schemas import (
    RecommendationResponse,
    UserSegmentResponse,
    MetricsResponse,
    MarketBasketResponse,
)

router = APIRouter()


@router.get(
    "/",
    summary="API root",
    description="Endpoint inicial para validar que la API de recomendación está disponible.",
)
def root():
    return {"message": "Instacart Recommendation API"}


@router.get(
    "/health",
    summary="Health check",
    description="Valida que la API esté activa y respondiendo correctamente.",
)
def health():
    return {"status": "ok", "message": "API running"}


@router.get(
    "/recommend/{user_id}",
    response_model=RecommendationResponse,
    summary="Get product recommendations",
    description="Devuelve recomendaciones mock para un usuario.",
)
def recommend(user_id: int, n: int = 5):
    return build_recommendation_response(user_id, n)


@router.get(
    "/segment/{user_id}",
    response_model=UserSegmentResponse,
    summary="Get user segment",
    description="Devuelve el segmento asignado a un usuario.",
)
def user_segment(user_id: int):
    return build_user_segment_response(user_id)


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Get model metrics",
    description="Devuelve métricas mock de los modelos.",
)
def metrics():
    return build_metrics_response()


@router.get(
    "/market-basket",
    response_model=MarketBasketResponse,
    summary="Get market basket rules",
    description="Devuelve reglas mock de Market Basket.",
)
def market_basket():
    return build_market_basket_response()
from fastapi import APIRouter
from pydantic import BaseModel

from api.services import (
    build_recommendation_response,
    build_user_segment_response,
    build_metrics_response,
)

router = APIRouter()


class RecommendationRequest(BaseModel):
    user_id: int
    product_ids: list[int] = []
    n: int = 10


@router.get("/")
def root():
    return {"message": "Instacart Recommendation API"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/segment/{user_id}")
def user_segment(user_id: int):
    return build_user_segment_response(user_id)


@router.get("/metrics")
def metrics():
    return build_metrics_response()


@router.post("/recommend")
def recommend(request: RecommendationRequest):
    return build_recommendation_response(
        user_id=request.user_id,
        product_ids=request.product_ids,
        n=request.n,
    )
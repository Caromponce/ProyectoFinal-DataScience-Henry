from pydantic import BaseModel


class Recommendation(BaseModel):
    product_id: int
    product_name: str
    score: float


class RecommendationResponse(BaseModel):
    user_id: int
    segment: str
    strategy: str
    strategy_name: str
    objective: str
    recommendations: list[Recommendation]


class UserFeatures(BaseModel):
    order_count: int
    avg_cart_size: float
    reorder_rate: float


class UserSegmentResponse(BaseModel):
    user_id: int
    segment: str
    features: UserFeatures


class ModelMetrics(BaseModel):
    model: str
    recall_at_10: float | None = None
    ndcg_at_10: float | None = None
    coverage: float | None = None
    rules_count: int | None = None
    avg_lift: float | None = None
    pr_auc: float | None = None
    f1: float | None = None


class MetricsResponse(BaseModel):
    total_users: int
    total_products: int
    total_interactions: int
    sparsity: float
    models: list[ModelMetrics]


class MarketBasketRule(BaseModel):
    antecedent: str
    consequent: str
    support: float
    confidence: float
    lift: float


class MarketBasketResponse(BaseModel):
    rules: list[MarketBasketRule]
from api.loader import models


SEGMENT_STRATEGY = {
    "Clientes sin historial de compras": {
        "strategy": "popularity",
        "strategy_name": "Popularity Baseline",
        "objective": "Recomendar productos populares para usuarios sin historial.",
    },
    "Clientes Ocasionales": {
        "strategy": "item_item_cf",
        "strategy_name": "Item-Item Collaborative Filtering",
        "objective": "Recomendar productos similares según historial de compras.",
    },
    "Clientes Leales o frecuentes": {
        "strategy": "reorder_prediction",
        "strategy_name": "Reorder Prediction",
        "objective": "Predecir recompra de productos ya conocidos por el usuario.",
    },
    "Clientes de canasta grande": {
        "strategy": "market_basket",
        "strategy_name": "Market Basket Analysis",
        "objective": "Recomendar productos complementarios según carrito.",
    },
}


def get_user_segment(user_id: int) -> str:
    return models.segmenter.predict(user_id)


def build_user_segment_response(user_id: int) -> dict:
    segment = get_user_segment(user_id)
    return {
        "user_id": user_id,
        "segment": segment,
        "strategy": SEGMENT_STRATEGY.get(segment, {}),
    }


def recommend_by_popularity(n: int = 10) -> dict:
    return {
        "strategy": "popularity",
        "recommendations": models.popularity.recommend(n),
    }


def recommend_by_item_item(product_ids: list[int], n: int = 10) -> dict:
    recommendations = models.item_item.recommend(product_ids, top_n=n)
    return {
        "strategy": "item_item_cf",
        "input_products": product_ids,
        "recommendations": recommendations,
    }


def recommend_by_market_basket_products(product_ids: list[int], n: int = 10) -> dict:
    recommendations = models.mba_products.recommend(product_ids, top_n=n)
    return {
        "strategy": "market_basket_products",
        "input_products": product_ids,
        "recommendations": recommendations,
    }


def recommend_by_market_basket_aisles(product_ids: list[int], n: int = 10) -> dict:
    recommendations = models.mba_aisles.recommend(product_ids, top_n=n)
    return {
        "strategy": "market_basket_aisles",
        "input_products": product_ids,
        "recommendations": recommendations,
    }


def predict_reorder(user_id: int, product_ids: list[int]) -> dict:
    predictions = models.reorder.predict(user_id=user_id, product_ids=product_ids)
    return {
        "strategy": "reorder_prediction",
        "user_id": user_id,
        "input_products": product_ids,
        "predictions": predictions,
    }


def build_recommendation_response(
    user_id: int,
    product_ids: list[int] | None = None,
    n: int = 10,
) -> dict:
    segment = get_user_segment(user_id)
    strategy_config = SEGMENT_STRATEGY.get(segment, {})

    if segment == "Clientes sin historial de compras":
        result = recommend_by_popularity(n)

    elif segment == "Clientes Ocasionales":
        result = recommend_by_item_item(product_ids or [], n)

    elif segment == "Clientes de canasta grande":
        result = recommend_by_market_basket_products(product_ids or [], n)

    elif segment == "Clientes Leales o frecuentes":
        result = predict_reorder(user_id, product_ids or [])

    else:
        result = recommend_by_popularity(n)

    return {
        "user_id": user_id,
        "segment": segment,
        "strategy": strategy_config.get("strategy", result.get("strategy")),
        "strategy_name": strategy_config.get("strategy_name"),
        "objective": strategy_config.get("objective"),
        "result": result,
    }


def build_metrics_response() -> dict:
    return {
        "available_models": [
            "kmeans_segmenter",
            "popularity",
            "market_basket_products",
            "market_basket_aisles",
            "item_item_cf",
            "reorder_prediction",
        ],
        "status": "models_loaded",
    }
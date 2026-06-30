SEGMENT_STRATEGY = {
    "Nuevo": {
        "strategy": "popularity",
        "strategy_name": "Popularity Model",
        "objective": "Resolver cold start recomendando productos populares",
    },
    "Ocasional": {
        "strategy": "item_item_cf",
        "strategy_name": "Item-Item Collaborative Filtering",
        "objective": "Personalizar con pocas compras históricas",
    },
    "Frecuente": {
        "strategy": "market_basket",
        "strategy_name": "Market Basket Analysis",
        "objective": "Impulsar cross-selling con productos complementarios",
    },
    "Leal": {
        "strategy": "reorder_prediction",
        "strategy_name": "Reorder Prediction",
        "objective": "Anticipar compras recurrentes y mejorar retención",
    },
}


def get_user_segment(user_id: int) -> str:
    segments = ["Nuevo", "Ocasional", "Frecuente", "Leal"]
    return segments[user_id % 4]


def get_mock_recommendations(n: int = 5) -> list[dict]:
    products = [
        {
            "product_id": 24852,
            "product_name": "Organic Bananas",
            "score": 0.92,
        },
        {
            "product_id": 13176,
            "product_name": "Bag of Organic Bananas",
            "score": 0.88,
        },
        {
            "product_id": 21137,
            "product_name": "Organic Strawberries",
            "score": 0.84,
        },
        {
            "product_id": 21903,
            "product_name": "Organic Baby Spinach",
            "score": 0.80,
        },
        {
            "product_id": 47209,
            "product_name": "Organic Hass Avocado",
            "score": 0.77,
        },
    ]

    return products[:n]


def build_recommendation_response(user_id: int, n: int = 5) -> dict:
    segment = get_user_segment(user_id)
    strategy = SEGMENT_STRATEGY[segment]

    return {
        "user_id": user_id,
        "segment": segment,
        "strategy": strategy["strategy"],
        "strategy_name": strategy["strategy_name"],
        "objective": strategy["objective"],
        "recommendations": get_mock_recommendations(n),
    }


def build_user_segment_response(user_id: int) -> dict:
    return {
        "user_id": user_id,
        "segment": get_user_segment(user_id),
        "features": {
            "order_count": 28,
            "avg_cart_size": 9.4,
            "reorder_rate": 0.72,
        },
    }

def build_metrics_response() -> dict:
    return {
        "total_users": 10000,
        "total_products": 32566,
        "total_interactions": 2203808,
        "sparsity": 99.7365,
        "models": [
            {
                "model": "Popularity",
                "recall_at_10": 0.046,
                "ndcg_at_10": None,
                "coverage": 0.12,
            },
            {
                "model": "Item-Item CF",
                "recall_at_10": 0.066,
                "ndcg_at_10": 0.081,
                "coverage": 0.35,
            },
            {
                "model": "Market Basket",
                "rules_count": 150,
                "avg_lift": 1.8,
            },
            {
                "model": "Reorder Prediction",
                "pr_auc": 0.74,
                "f1": 0.61,
            },
        ],
    }


def build_market_basket_response() -> dict:
    return {
        "rules": [
            {
                "antecedent": "Organic Banana",
                "consequent": "Whole Milk",
                "support": 0.04,
                "confidence": 0.42,
                "lift": 1.85,
            },
            {
                "antecedent": "Bag of Organic Bananas",
                "consequent": "Organic Strawberries",
                "support": 0.03,
                "confidence": 0.36,
                "lift": 1.62,
            },
        ],
    }
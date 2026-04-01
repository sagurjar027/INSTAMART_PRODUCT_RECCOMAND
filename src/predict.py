from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data" / "raw" / "processed"


@lru_cache(maxsize=1)
def load_recommendation_assets():
    model = joblib.load(MODELS_DIR / "xgb_model.pkl")
    features = joblib.load(MODELS_DIR / "features.pkl")
    user_features = pd.read_csv(DATA_DIR / "user_features.csv")
    product_features = pd.read_csv(DATA_DIR / "product_features.csv")
    user_product = pd.read_csv(DATA_DIR / "user_product.csv")
    products = pd.read_csv(DATA_DIR / "products.csv")
    return model, features, user_features, product_features, user_product, products


@lru_cache(maxsize=1)
def load_dashboard_assets():
    user_features = pd.read_csv(DATA_DIR / "user_features.csv")
    product_features = pd.read_csv(DATA_DIR / "product_features.csv")
    products = pd.read_csv(DATA_DIR / "products.csv")
    return user_features, product_features, products


def recommend(user_id: int, top_n: int = 10) -> pd.DataFrame | None:
    model, features, user_features, product_features, user_product, products = load_recommendation_assets()

    user_data = user_product[user_product["user_id"] == user_id].copy()
    if user_data.empty:
        return None

    user_data = user_data.merge(user_features, on="user_id", how="left")
    user_data = user_data.merge(product_features, on="product_id", how="left")

    feature_matrix = user_data.loc[:, features]
    user_data["prob"] = model.predict_proba(feature_matrix)[:, 1]

    ranked_products = (
        user_data.sort_values("prob", ascending=False)
        .head(top_n)
        .merge(products, on="product_id", how="left")
    )

    return ranked_products[
        [
            "product_id",
            "product_name",
            "prob",
            "up_order_count",
            "up_reorder_count",
            "product_orders",
            "product_reorder_rate",
            "aisle_id",
            "department_id",
        ]
    ]


def get_user_profile(user_id: int) -> dict | None:
    user_features, _, _ = load_dashboard_assets()
    user_row = user_features[user_features["user_id"] == user_id]
    if user_row.empty:
        return None

    row = user_row.iloc[0]
    return {
        "user_id": int(row["user_id"]),
        "total_orders": int(row["total_orders"]),
        "total_products": int(row["total_products"]),
        "reorder_ratio": float(row["reorder_ratio"]),
    }


def get_dashboard_overview(top_n: int = 10) -> dict:
    user_features, product_features, products = load_dashboard_assets()

    popular_products = (
        product_features.merge(products[["product_id", "product_name"]], on="product_id", how="left")
        .sort_values("product_orders", ascending=False)
        .head(top_n)
    )

    reliable_products = (
        product_features[product_features["product_orders"] >= 500]
        .merge(products[["product_id", "product_name"]], on="product_id", how="left")
        .sort_values("product_reorder_rate", ascending=False)
        .head(top_n)
    )

    return {
        "summary": {
            "total_users": int(user_features["user_id"].nunique()),
            "total_products": int(products["product_id"].nunique()),
            "avg_orders_per_user": float(user_features["total_orders"].mean()),
            "avg_products_per_user": float(user_features["total_products"].mean()),
            "avg_reorder_ratio": float(user_features["reorder_ratio"].mean()),
            "median_reorder_ratio": float(user_features["reorder_ratio"].median()),
        },
        "user_features": user_features,
        "product_features": product_features,
        "popular_products": popular_products,
        "reliable_products": reliable_products,
    }

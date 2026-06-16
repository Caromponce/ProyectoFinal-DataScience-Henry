"""
cargar_datos.py
Carga los datasets de Instacart Market Basket Analysis
"""

import pandas as pd
import os
import time

# ── Ruta base ─────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


# ── Dtypes optimizados para reducir uso de memoria ────────────────────────────
# Nota: pandas no soporta float16 al leer CSV; se usa float32 como mínimo.
DTYPES = {
    "aisles": {
        "aisle_id": "int8",
        "aisle":    "category",
    },
    "departments": {
        "department_id": "int8",
        "department":    "category",
    },
    "orders": {
        "order_id":               "int32",
        "user_id":                "int32",
        "eval_set":               "category",
        "order_number":           "int16",
        "order_dow":              "int8",
        "order_hour_of_day":      "int8",
        "days_since_prior_order": "float32",   
    },
    "products": {
        "product_id":    "int32",
        "product_name":  "object",
        "aisle_id":      "int8",
        "department_id": "int8",
    },
    "order_products__prior": {
        "order_id":          "int32",
        "product_id":        "int32",
        "add_to_cart_order": "int16",
        "reordered":         "int8",
    },
    "order_products__train": {
        "order_id":          "int32",
        "product_id":        "int32",
        "add_to_cart_order": "int16",
        "reordered":         "int8",
    },
}


def load_csv(name: str, verbose: bool = True) -> pd.DataFrame:
    """Carga un CSV por nombre (sin extensión) con dtypes optimizados."""
    filepath = os.path.join(DATA_PATH, f"{name}.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No se encontró: {filepath}")

    t0 = time.time()
    df = pd.read_csv(filepath, dtype=DTYPES.get(name))
    elapsed = time.time() - t0

    if verbose:
        mem_mb = df.memory_usage(deep=True).sum() / 1024 ** 2
        print(f"✔ {name:<30} {df.shape[0]:>10,} filas  |  {df.shape[1]} cols  |  "
              f"{mem_mb:.1f} MB  |  {elapsed:.1f}s")

    return df


def load_all(verbose: bool = True) -> dict:
    """
    Carga todos los CSVs y los devuelve en un diccionario.

    Retorna
    -------
    dict con claves:
        'aisles', 'departments', 'orders', 'products',
        'order_products_prior', 'order_products_train'
    """
    if verbose:
        print("=" * 70)
        print("Cargando datasets — Instacart Market Basket Analysis")
        print("=" * 70)

    datasets = {}

    # Tablas pequeñas
    datasets["aisles"]       = load_csv("aisles",       verbose)
    datasets["departments"]  = load_csv("departments",  verbose)
    datasets["products"]     = load_csv("products",     verbose)

    # Tabla mediana
    datasets["orders"]       = load_csv("orders",       verbose)

    # Tablas grandes
    datasets["order_products_prior"] = load_csv("order_products__prior", verbose)
    datasets["order_products_train"] = load_csv("order_products__train", verbose)

    if verbose:
        print("=" * 70)
        total_mb = sum(
            df.memory_usage(deep=True).sum() for df in datasets.values()
        ) / 1024 ** 2
        print(f"Total en memoria: {total_mb:.1f} MB")
        print("=" * 70)

    return datasets


# ── Ejecución directa ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    dfs = load_all(verbose=True)

    # Asignar variables individuales para uso interactivo
    aisles                 = dfs["aisles"]
    departments            = dfs["departments"]
    products               = dfs["products"]
    orders                 = dfs["orders"]
    order_products_prior   = dfs["order_products_prior"]
    order_products_train   = dfs["order_products_train"]

    print("\nVariables disponibles:")
    for name, df in dfs.items():
        print(f"  {name}: {df.shape}")
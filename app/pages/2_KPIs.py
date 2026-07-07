# importar librerías
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.styles import inject_css
from src.ui import henry_title, henry_tag


st.set_page_config(
    page_title="KPIs",
    page_icon="📊",
    layout="wide"
)

inject_css()

BASE_DIR = Path(__file__).resolve().parents[2]
METRICS_PATH = BASE_DIR / "data" / "processed" / "dashboard_metrics.json"


@st.cache_data
def load_metrics():
    with open(METRICS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


with st.sidebar:
    st.image("assets/logo_data_horizon.png", width=120)


henry_tag("Evaluación de modelos")
henry_title("KPIs del Sistema")

st.write(
    """
    El sistema implementa una arquitectura híbrida de recomendación:
    la API selecciona automáticamente el modelo más adecuado según
    el comportamiento del usuario y el contexto de compra.
    """
)

st.divider()

data = load_metrics()


# ==========================
# KPIs generales
# ==========================

c1, c2, c3, c4 = st.columns(4)

c1.metric("Usuarios", f"{data['total_users']:,}".replace(",", "."))
c2.metric("Productos", f"{data['total_products']:,}".replace(",", "."))
c3.metric("Interacciones", f"{data['total_interactions']:,}".replace(",", "."))
c4.metric("Sparsity", f"{data['sparsity']:.2f}%")

st.divider()


# ==========================
# Arquitectura del recomendador
# ==========================

henry_tag("Arquitectura híbrida")

st.subheader("🧠 Estrategias de recomendación")

router_df = pd.DataFrame(data["recommendation_router"])

router_df = router_df.rename(
    columns={
        "segment": "Segmento / Caso de uso",
        "strategy": "Modelo seleccionado",
        "objective": "Objetivo"
    }
)

st.dataframe(
    router_df,
    use_container_width=True,
    hide_index=True
)

st.info(
    """
    El valor del sistema no está en elegir un único modelo ganador, sino en
    seleccionar la estrategia correcta según el tipo de usuario y el carrito.
    """
)

st.divider()


# ==========================
# Segmentación
# ==========================

henry_tag("Segmentación")

st.subheader("👥 Métricas del modelo K-Means")

kmeans = data["kmeans"]

k1, k2, k3 = st.columns(3)

k1.metric("Clusters", kmeans["k"])
k2.metric("Silhouette Score", f"{kmeans['silhouette']:.4f}")
k3.metric("Davies-Bouldin", f"{kmeans['davies_bouldin']:.4f}")

st.divider()


# ==========================
# Performance de modelos
# ==========================

henry_tag("Performance")

st.subheader("📈 Desempeño de modelos")

models_df = pd.DataFrame(data["models"])

performance_df = models_df.copy()

performance_df["Valor"] = performance_df["value"].apply(
    lambda x: "-"
    if pd.isna(x)
    else f"{x:.4f}"
    if x < 1
    else f"{int(x):,}".replace(",", ".")
)

performance_table = performance_df.rename(
    columns={
        "model": "Modelo",
        "use_case": "Caso de uso",
        "main_metric": "Métrica principal",
        "notes": "Notas"
    }
)

st.dataframe(
    performance_table[
        [
            "Modelo",
            "Caso de uso",
            "Métrica principal",
            "Valor",
            "Notas"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.divider()


# ==========================
# Explorador de modelos
# ==========================

st.subheader("🔎 Explorador interactivo de modelos")

selected_model = st.selectbox(
    "Seleccioná un modelo",
    performance_table["Modelo"].tolist()
)


selected = performance_table[
    performance_table["Modelo"] == selected_model
].iloc[0]

MODEL_INFO = {

    "Popularity Baseline": {
        "descripcion":
            "Modelo no personalizado utilizado para resolver el problema de cold-start. "
            "Recomienda los productos con mayor popularidad histórica cuando un cliente aún no posee historial de compras.",

        "porque":
            "Fue incorporado para garantizar recomendaciones desde la primera interacción del usuario.",

        "interpretacion":
            "No requiere entrenamiento ni métricas tradicionales; actúa como línea base del sistema."
    },

    "Item-Item Collaborative Filtering": {
        "descripcion":
            "Calcula similitud entre productos utilizando el historial de compras de los clientes. "
            "Cuando un usuario compra un producto, recomienda otros productos similares.",

        "porque":
            "Obtuvo Recall@10 = 0.0660, superando ampliamente al baseline (0.0460).",

        "interpretacion":
            "Recall@10 mide qué porcentaje de productos realmente comprados aparecen dentro de las primeras diez recomendaciones."
    },

    "Market Basket Analysis (Products)": {
        "descripcion":
            "Descubre asociaciones frecuentes entre productos mediante FP-Growth y reglas de asociación.",

        "porque":
            "Permite generar recomendaciones de cross-selling y creación de combos comerciales.",

        "interpretacion":
            "Su desempeño se evalúa mediante la cantidad y calidad de reglas generadas (Support, Confidence y Lift), no mediante Recall."
    },

    "Market Basket Analysis (Aisles)": {
        "descripcion":
            "Extiende Market Basket Analysis al nivel de pasillos para detectar categorías que suelen comprarse conjuntamente.",

        "porque":
            "Permite recomendar categorías completas y diseñar promociones cruzadas.",

        "interpretacion":
            "Se analiza mediante reglas de asociación entre categorías utilizando FP-Growth."
    },

    "Reorder Prediction (XGBoost)": {
        "descripcion":
            "Modelo supervisado entrenado para estimar la probabilidad de recompra de cada producto por cliente.",

        "porque":
            "Fue el modelo con mejor desempeño para clientes leales gracias a su capacidad para capturar patrones complejos.",

        "interpretacion":
            "La métrica principal es PR-AUC, especialmente adecuada para problemas con clases desbalanceadas."
    }
}

info = MODEL_INFO.get(
    selected["Modelo"],
    {
        "descripcion": selected["Notas"],
        "porque": "-",
        "interpretacion": "-"
    }
)

st.markdown(
    f"""
<div class="henry-card">

### {selected["Modelo"]}

**Caso de uso**

{selected["Caso de uso"]}

---

**Métrica principal**

{selected["Métrica principal"]}

**Resultado obtenido**

{selected["Valor"]}

---

**¿Qué hace este modelo?**

{info["descripcion"]}

---

**¿Por qué fue seleccionado?**

{info["porque"]}

---

**¿Cómo interpretar este resultado?**

{info["interpretacion"]}

</div>
""",
    unsafe_allow_html=True
)

st.divider()


# ==========================
# Reorder Prediction
# ==========================

henry_tag("Modelo supervisado")

st.subheader("🏆 Reorder Prediction - XGBoost")

reorder = models_df[
    models_df["model"] == "Reorder Prediction (XGBoost)"
].iloc[0]

r1, r2, r3, r4 = st.columns(4)

r1.metric("PR-AUC", f"{reorder['value']:.4f}")
r2.metric("Precision", f"{reorder['precision']:.4f}")
r3.metric("Recall", f"{reorder['recall']:.4f}")
r4.metric("F1 Score", f"{reorder['f1']:.4f}")

st.success(
    f"""
    **Modelo supervisado ganador:** XGBoost.

    Fue seleccionado por su desempeño en **PR-AUC = {reorder['value']:.4f}**
    y se utiliza para recomendar productos con alta probabilidad de recompra
    en clientes leales.
    """
)

st.divider()


# ==========================
# Conclusiones
# ==========================

henry_tag("Conclusiones")

st.markdown(
    """
### ✅ Lectura de resultados

- El sistema no utiliza un único algoritmo de recomendación.
- La API identifica el tipo de usuario y selecciona automáticamente la estrategia más adecuada.
- Los usuarios sin historial reciben recomendaciones basadas en popularidad.
- Los clientes ocasionales reciben recomendaciones mediante Item-Item Collaborative Filtering.
- Los clientes leales utilizan un modelo supervisado de predicción de recompra.
- Para carritos con múltiples productos se complementa la recomendación mediante Market Basket Analysis.
"""
)
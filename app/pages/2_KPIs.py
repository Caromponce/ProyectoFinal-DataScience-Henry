# importar librerías
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
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

st.subheader("📈 Métricas comparables de desempeño")

models_df = pd.DataFrame(data["models"])

performance_df = models_df.copy()
performance_df["Valor"] = performance_df["value"].apply(
    lambda x: "-" if pd.isna(x) else f"{x:.4f}" if x < 1 else f"{int(x):,}".replace(",", ".")
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

# Solo se grafican las métricas porcentuales comparables
chart_df = models_df[
    models_df["value"].notna() & (models_df["value"] < 1)
].copy()

if not chart_df.empty:
    chart_df["value_pct"] = chart_df["value"] * 100

    fig = px.bar(
        chart_df,
        x="model",
        y="value_pct",
        text=chart_df["value_pct"].round(2).astype(str) + "%",
        color="model",
        color_discrete_map={
            "Item-Item Collaborative Filtering": "#7C3AED",
            "Reorder Prediction (XGBoost)": "#F2E40C"
        }
    )

    fig.update_traces(
        textposition="outside",
        marker_line_color="#1A1A1A",
        marker_line_width=1
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Inter",
            color="#1A1A1A",
            size=15
        ),
        xaxis_title="Modelo",
        yaxis_title="Valor (%)",
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(
            range=[0, chart_df["value_pct"].max() * 1.18]
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "El gráfico compara únicamente métricas porcentuales (Recall@10 y PR-AUC). "
        "Los modelos de Market Basket Analysis se evalúan por la cantidad de reglas generadas, "
        "por lo que esa información se presenta en la tabla superior."
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
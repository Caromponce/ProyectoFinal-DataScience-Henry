# importar librerías
import streamlit as st
import pandas as pd
import plotly.express as px

from src.api_client import get_metrics
from src.styles import inject_css
from src.ui import henry_title, henry_tag

st.set_page_config(
    page_title="KPIs",
    page_icon="📊",
    layout="wide"
)

inject_css()

with st.sidebar:
    st.image("assets/logo_data_horizon.png", width=120)

henry_tag("Evaluación de modelos")
henry_title("KPIs del Sistema")

st.write(
    "Métricas generales del dataset y comparación inicial de modelos."
)

st.divider()

data = get_metrics()

# ==========================
# KPIs
# ==========================

c1, c2, c3, c4 = st.columns(4)

c1.metric("Usuarios", f"{data['total_users']:,}")
c2.metric("Productos", f"{data['total_products']:,}")
c3.metric("Interacciones", f"{data['total_interactions']:,}")
c4.metric("Sparsity", f"{data['sparsity']:.2f}%")

st.divider()

henry_tag("Performance")

st.subheader("📈 Comparación de modelos")

df = pd.DataFrame(data["models"])

# ==========================
# colores corporativos
# ==========================

colors = [
    "#7C3AED",   # Baseline Popularity
    "#7C3AED",   # User-Based CF
    "#7C3AED",   # Market Basket
    "#E8472B"    # Reorder Prediction ⭐
]

df["Recall"] = (
    df["recall_at_10"] * 100
).round(1).astype(str) + "%"

fig = px.bar(
    df,
    x="model",
    y="recall_at_10",
    text="Recall"
)

fig.update_traces(
    marker_color=colors,
    textposition="outside"
)

fig.update_layout(

    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="Inter",
        color="#1A1A1A",
        size=15
    ),

    yaxis_title="Recall@10 (%)",
    xaxis_title="",

    # NUEVO
    xaxis=dict(
        showgrid=False
    ),

    yaxis=dict(
        showgrid=False,
        zeroline=False
    ),

    showlegend=False,

    margin=dict(
        l=20,
        r=20,
        t=30,
        b=20
    )
)

left, right = st.columns([4,1])

with left:
    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.success(
        """
🏆 **Mejor modelo**

**Reorder Prediction**

Recall@10 = **7.1%**
"""
    )

st.divider()

st.subheader("📋 Tabla comparativa")

table = df.copy()

table["Recall@10"] = (
    table["recall_at_10"]*100
).round(1).astype(str)+"%"

table = table.rename(
    columns={
        "model":"Modelo"
    }
)

st.dataframe(
    table[["Modelo","Recall@10"]],
    use_container_width=True,
    hide_index=True
)
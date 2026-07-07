# importar librerías
import streamlit as st
import pandas as pd
import plotly.express as px

from src.api_client import get_user_segment
from src.styles import inject_css
from src.ui import henry_title, henry_tag


st.set_page_config(
    page_title="Segmentación",
    page_icon="👥",
    layout="wide"
)

inject_css()

with st.sidebar:
    st.image("assets/logo_data_horizon.png", width=150)
    st.markdown(
        """
        <h2>DATA HORIZON</h2>
        <p>Transformamos datos<br>en decisiones</p>
        """,
        unsafe_allow_html=True
    )
    st.divider()


henry_tag("Clustering de usuarios")
henry_title("Segmentación de Usuarios")

st.markdown(
    """
    La segmentación combina un modelo **K-Means** con reglas de negocio para
    clasificar a los clientes según su comportamiento de compra y seleccionar
    la estrategia de recomendación más adecuada.
    """
)

st.divider()


# ==========================
# Datos de segmentos
# ==========================

segments_data = [
    {
        "segment": "Clientes sin historial",
        "users": None,
        "percentage": None,
        "strategy": "Popularity Model",
        "orders_avg": "Sin historial suficiente",
        "reorder_rate": "-",
        "basket_avg": "-"
    },
    {
        "segment": "Clientes Ocasionales",
        "users": 5620,
        "percentage": 56.2,
        "strategy": "Item-Item Collaborative Filtering",
        "orders_avg": 9.28,
        "reorder_rate": "39.0%",
        "basket_avg": 8.29
    },
    {
        "segment": "Clientes Leales",
        "users": 4380,
        "percentage": 43.8,
        "strategy": "Reorder Prediction",
        "orders_avg": 31.10,
        "reorder_rate": "61.3%",
        "basket_avg": 12.30
    },
    {
        "segment": "Canasta grande",
        "users": None,
        "percentage": None,
        "strategy": "Market Basket Analysis",
        "orders_avg": "Según carrito",
        "reorder_rate": "-",
        "basket_avg": "Alto"
    }
]

segments_df = pd.DataFrame(segments_data)


# ==========================
# Consulta por cliente
# ==========================

st.subheader("🔎 Consultar segmento por cliente")

col_user, col_button = st.columns([2, 1])

with col_user:
    user_id = st.number_input(
        "Número de cliente",
        min_value=1,
        value=3,
        step=1
    )

with col_button:
    st.write("")
    st.write("")
    consultar = st.button("Consultar API", use_container_width=True)

if consultar:
    try:
        segment_response = get_user_segment(user_id)
        segment_name = segment_response.get("segment", "Sin segmento")

        if segment_name == "Clientes Leales o frecuentes":
            segment_name = "Clientes Leales"

        strategy = segment_response.get("strategy", {})

        st.markdown(
            f"""
            <div class="henry-card">
                <h3>Cliente {segment_response["user_id"]}</h3>
                <p><strong>Segmento detectado:</strong> {segment_name}</p>
                <p><strong>Estrategia recomendada:</strong> {strategy.get("strategy_name", "Sin dato")}</p>
                <p><strong>Objetivo:</strong> {strategy.get("objective", "Sin dato")}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    except Exception as error:
        st.error("No se pudo consultar la API.")
        st.exception(error)

st.divider()


# ==========================
# Explorador interactivo
# ==========================

st.subheader("🔎 Explorador interactivo de segmentos")

selected_segment = st.selectbox(
    "Seleccioná un segmento",
    segments_df["segment"].tolist(),
    index=1
)

selected_row = segments_df[
    segments_df["segment"] == selected_segment
].iloc[0]

users_value = (
    "-"
    if pd.isna(selected_row["users"])
    else f"{int(selected_row['users']):,}".replace(",", ".")
)

percentage_value = (
    "Regla de negocio"
    if pd.isna(selected_row["percentage"])
    else f"{selected_row['percentage']}%"
)

st.markdown(
    f"""
    <div class="henry-card">
        <h3>{selected_row["segment"]}</h3>
        <p><strong>Clientes:</strong> {users_value}</p>
        <p><strong>Participación:</strong> {percentage_value}</p>
        <p><strong>Modelo recomendado:</strong> {selected_row["strategy"]}</p>
        <p><strong>Pedidos promedio:</strong> {selected_row["orders_avg"]}</p>
        <p><strong>Tasa de recompra:</strong> {selected_row["reorder_rate"]}</p>
        <p><strong>Carrito promedio:</strong> {selected_row["basket_avg"]}</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ==========================
# Segmentos funcionales
# ==========================

st.subheader("📌 Segmentos funcionales del sistema")

cols = st.columns(4)

colors = {
    "Clientes sin historial": "🟢",
    "Clientes Ocasionales": "🔵",
    "Clientes Leales": "🔴",
    "Canasta grande": "🛒"
}

for i, row in segments_df.iterrows():
    with cols[i]:
        value = (
            f"{row['percentage']}%"
            if pd.notna(row["percentage"])
            else "Regla"
        )

        st.markdown(
            f"""
            <div class="henry-card">
                <h3>{colors[row["segment"]]} {row["segment"]}</h3>
                <p><strong>Participación:</strong> {value}</p>
                <p><strong>Modelo:</strong> {row["strategy"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.info(
    """
    El K-Means encontró dos grupos principales: **Clientes Ocasionales** y
    **Clientes Leales**. Además, el sistema incorpora reglas de negocio para
    clientes sin historial suficiente y para activar recomendaciones de
    **Market Basket Analysis** cuando el carrito permite sugerir productos asociados.
    """
)

st.divider()


# ==========================
# Distribución
# ==========================

henry_tag("Distribución")

st.subheader("📊 Distribución real del K-Means")

cluster_df = segments_df[
    segments_df["percentage"].notna()
].copy()

segment_colors = {
    "Clientes Ocasionales": "#7C3AED",
    "Clientes Leales": "#E8472B"
}

fig = px.bar(
    cluster_df,
    x="segment",
    y="users",
    text="users",
    color="segment",
    color_discrete_map=segment_colors
)

fig.update_traces(textposition="outside")

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(
        family="Inter",
        color="#1A1A1A",
        size=15
    ),
    xaxis_title="Segmento",
    yaxis_title="Clientes",
    showlegend=False,
    margin=dict(l=20, r=20, t=30, b=20)
)

st.plotly_chart(fig, use_container_width=True)

st.divider()


# ==========================
# Detalle
# ==========================

henry_tag("Detalle")

st.subheader("📋 Perfil de segmentos y reglas")

table = segments_df.rename(
    columns={
        "segment": "Segmento",
        "users": "Clientes",
        "percentage": "%",
        "strategy": "Modelo recomendado",
        "orders_avg": "Pedidos promedio",
        "reorder_rate": "Tasa de recompra",
        "basket_avg": "Carrito promedio"
    }
)

st.dataframe(
    table[
        [
            "Segmento",
            "Clientes",
            "%",
            "Pedidos promedio",
            "Tasa de recompra",
            "Carrito promedio",
            "Modelo recomendado"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.divider()


# ==========================
# Métricas del clustering
# ==========================

henry_tag("Métricas del clustering")

c1, c2, c3 = st.columns(3)

c1.metric("Cantidad de clusters", "2")
c2.metric("Silhouette Score", "0.3276")
c3.metric("Davies-Bouldin", "1.1389")

st.divider()


# ==========================
# Interpretación
# ==========================

henry_tag("Interpretación")

st.markdown(
    """
### 🧠 ¿Por qué segmentamos?

En lugar de recomendar lo mismo a todos los clientes, el sistema identifica
su comportamiento de compra y selecciona la estrategia más adecuada.

- **Clientes sin historial** → Popularity Model
- **Clientes Ocasionales** → Item-Item Collaborative Filtering
- **Clientes Leales** → Reorder Prediction
- **Canasta grande** → Market Basket Analysis como estrategia complementaria

Este enfoque permite personalizar las recomendaciones según el nivel de actividad,
la calidad del historial disponible y los productos presentes en el carrito.
"""
)
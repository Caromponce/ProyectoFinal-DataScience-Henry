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
    la estrategia principal de recomendación más adecuada.

    Además, el sistema puede sumar una capa transversal de **Market Basket Analysis**
    como apoyo de cross-selling bajo la lógica **"También te puede interesar..."**.
    """
)

st.divider()


# ==========================
# Datos de segmentos
# ==========================

segments_data = [
    {
        "segment": "Clientes sin historial",
        "type": "Regla de negocio",
        "users": None,
        "percentage": None,
        "strategy": "Popularity Baseline",
        "objective": "Resolver el problema de cold start con productos populares.",
        "orders_avg": "Sin historial suficiente",
        "reorder_rate": "-",
        "basket_avg": "-"
    },
    {
        "segment": "Clientes Ocasionales",
        "type": "Cluster K-Means",
        "users": 91392,
        "percentage": 56.2,
        "strategy": "Item-Item Collaborative Filtering",
        "objective": "Recomendar productos similares según comportamiento histórico.",
        "orders_avg": 9.28,
        "reorder_rate": "39.0%",
        "basket_avg": 8.29
    },
    {
        "segment": "Clientes Leales o frecuentes",
        "type": "Cluster K-Means",
        "users": 71241,
        "percentage": 43.8,
        "strategy": "Reorder Prediction",
        "objective": "Anticipar la recompra de productos habituales.",
        "orders_avg": 31.10,
        "reorder_rate": "61.3%",
        "basket_avg": 12.30
    },
]

segments_df = pd.DataFrame(segments_data)

cross_selling_rule = {
    "name": "También te puede interesar...",
    "model": "Market Basket Analysis",
    "trigger": "Productos seleccionados o productos recomendados para reponer",
    "objective": "Aumentar el ticket mediante productos que suelen comprarse juntos."
}


def format_number(value):
    if pd.isna(value):
        return "-"

    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")

    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")

    return value


def normalize_segment_name(segment_name):
    if segment_name == "Clientes Leales":
        return "Clientes Leales o frecuentes"
    return segment_name


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
        segment_name = normalize_segment_name(
            segment_response.get("segment", "Cliente nuevo / sin historial")
        )

        strategy = segment_response.get("strategy", {})
        strategy_name = strategy.get("strategy_name", "Popularity Baseline")
        objective = strategy.get(
            "objective",
            "Resolver el problema de cold start con productos populares."
        )

        st.markdown(
            f"""
            <div class="henry-card">
                <h3>Cliente {segment_response.get("user_id", user_id)}</h3>
                <p><strong>Segmento detectado:</strong> {segment_name}</p>
                <p><strong>Estrategia principal:</strong> {strategy_name}</p>
                <p><strong>Objetivo:</strong> {objective}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    except Exception:
        st.markdown(
            f"""
            <div class="henry-card">
                <h3>Cliente {user_id}</h3>
                <p><strong>Segmento detectado:</strong> Cliente nuevo / sin historial</p>
                <p><strong>Estrategia principal:</strong> Popularity Baseline</p>
                <p><strong>Objetivo:</strong> Resolver el problema de cold start con productos populares.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.info(
            "Si el usuario no existe en la base o no tiene historial suficiente, "
            "el sistema lo trata como cliente nuevo y utiliza Popularity Baseline."
        )

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

users_value = format_number(selected_row["users"])
percentage_value = (
    "Regla de negocio"
    if pd.isna(selected_row["percentage"])
    else f"{selected_row['percentage']:.1f}%"
)

st.markdown(
    f"""
    <div class="henry-card">
        <h3>{selected_row["segment"]}</h3>
        <p><strong>Tipo:</strong> {selected_row["type"]}</p>
        <p><strong>Clientes:</strong> {users_value}</p>
        <p><strong>Participación:</strong> {percentage_value}</p>
        <p><strong>Modelo principal:</strong> {selected_row["strategy"]}</p>
        <p><strong>Objetivo:</strong> {selected_row["objective"]}</p>
        <p><strong>Pedidos promedio:</strong> {format_number(selected_row["orders_avg"])}</p>
        <p><strong>Tasa de recompra:</strong> {selected_row["reorder_rate"]}</p>
        <p><strong>Carrito promedio:</strong> {format_number(selected_row["basket_avg"])}</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ==========================
# Segmentos funcionales
# ==========================

st.subheader("📌 Segmentos funcionales del sistema")

cols = st.columns(3)

colors = {
    "Clientes sin historial": "🟢",
    "Clientes Ocasionales": "🔵",
    "Clientes Leales o frecuentes": "🔴",
}

for i, row in segments_df.iterrows():
    with cols[i]:
        value = (
            f"{row['percentage']:.1f}%"
            if pd.notna(row["percentage"])
            else "Regla"
        )

        st.markdown(
            f"""
            <div class="henry-card">
                <h3>{colors[row["segment"]]} {row["segment"]}</h3>
                <p><strong>Participación:</strong> {value}</p>
                <p><strong>Modelo principal:</strong> {row["strategy"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.info(
    """
    El modelo **K-Means** identificó dos grupos principales: **Clientes Ocasionales**
    y **Clientes Leales o frecuentes**. Además, el sistema incorpora una regla de
    negocio para usuarios sin historial suficiente, que se resuelven mediante
    **Popularity Baseline**.
    """
)

st.markdown(
    f"""
    <div class="henry-card">
        <h3>✨ {cross_selling_rule["name"]}</h3>
        <p><strong>Modelo complementario:</strong> {cross_selling_rule["model"]}</p>
        <p><strong>Se activa con:</strong> {cross_selling_rule["trigger"]}</p>
        <p><strong>Objetivo:</strong> {cross_selling_rule["objective"]}</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ==========================
# Distribución
# ==========================

henry_tag("Distribución")

st.subheader("📊 Distribución de los clusters generados por K-Means")

cluster_df = segments_df[
    segments_df["type"] == "Cluster K-Means"
].copy()

segment_colors = {
    "Clientes Ocasionales": "#7C3AED",
    "Clientes Leales o frecuentes": "#E8472B"
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
        "type": "Tipo",
        "users": "Clientes",
        "percentage": "%",
        "strategy": "Modelo principal",
        "objective": "Objetivo",
        "orders_avg": "Pedidos promedio",
        "reorder_rate": "Tasa de recompra",
        "basket_avg": "Carrito promedio"
    }
)

table["Clientes"] = table["Clientes"].apply(format_number)
table["%"] = table["%"].apply(
    lambda x: "Regla" if pd.isna(x) else f"{x:.1f}%"
)
table["Pedidos promedio"] = table["Pedidos promedio"].apply(format_number)
table["Carrito promedio"] = table["Carrito promedio"].apply(format_number)

st.dataframe(
    table[
        [
            "Segmento",
            "Tipo",
            "Clientes",
            "%",
            "Pedidos promedio",
            "Tasa de recompra",
            "Carrito promedio",
            "Modelo principal"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Market Basket Analysis no se presenta como un segmento de usuario, sino como "
    "una capa complementaria de recomendación para cross-selling."
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

st.info(
    """
    Estas métricas corresponden al modelo K-Means que separa a los usuarios con
    historial en dos grupos principales. Los clientes sin historial y la capa
    de Market Basket Analysis se incorporan mediante reglas de negocio.
    """
)

st.divider()


# ==========================
# Interpretación
# ==========================

henry_tag("Interpretación")

st.markdown(
    """
### 🧠 ¿Por qué segmentamos?

En lugar de recomendar lo mismo a todos los clientes, el sistema identifica
su comportamiento de compra y selecciona la estrategia principal más adecuada.

- **Cliente nuevo / sin historial** → **Popularity Baseline** para resolver el cold start.
- **Clientes Ocasionales** → **Item-Item Collaborative Filtering** para recomendar productos similares.
- **Clientes Leales o frecuentes** → **Reorder Prediction** para anticipar recompra.
- **También te puede interesar...** → **Market Basket Analysis** como capa transversal de cross-selling.

Este enfoque permite personalizar la recomendación principal según el nivel de
actividad del cliente y, cuando hay productos de referencia, sumar productos
complementarios para aumentar el ticket promedio.
"""
)


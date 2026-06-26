# importar librerías
import streamlit as st
import pandas as pd
import plotly.express as px

# importar cliente
from src.api_client import get_segments

# importar estilo Henry
from src.styles import inject_css
from src.ui import henry_title, henry_tag

# configuración
st.set_page_config(
    page_title="Segmentación",
    page_icon="👥",
    layout="wide"
)

inject_css()
 
with st.sidebar:

    st.image(
        "assets/logo_data_horizon.png",
        width=150
    )

    st.markdown(
        """
        <h2>DATA HORIZON</h2>

        <p>
        Transformamos datos<br>
        en decisiones
        </p>
        """,
        unsafe_allow_html=True
    )

    st.divider()

# ----------------------------
# Header
# ----------------------------

henry_tag("Clustering de usuarios")
henry_title("Segmentación de Usuarios")

st.markdown(
    """
    Los usuarios fueron agrupados según su comportamiento de compra.

    Cada segmento utiliza un motor de recomendación diferente para
    maximizar la calidad de las recomendaciones.
    """
)

st.divider()

# ----------------------------
# Datos
# ----------------------------

segments = get_segments()

segments_df = pd.DataFrame(
    segments["distribution"]
)

# ----------------------------
# Tarjetas
# ----------------------------

st.subheader("📌 Distribución de segmentos")

cols = st.columns(4)

colors = {
    "Nuevo": "🟢",
    "Ocasional": "🔵",
    "Frecuente": "🟡",
    "Leal": "🔴"
}

for i, row in segments_df.iterrows():

    with cols[i]:

        st.metric(
            label=f"{colors[row['segment']]} {row['segment']}",
            value=f"{row['percentage']}%"
        )

        st.caption(row["strategy"])

st.divider()

# ----------------------------
# Gráfico
# ----------------------------

henry_tag("Distribución")

st.subheader("📊 Cantidad de usuarios por segmento")

segment_colors = {
    "Nuevo": "#1F7A44",
    "Ocasional": "#7C3AED",
    "Frecuente": "#F2E40C",
    "Leal": "#E8472B"
}

fig = px.bar(
    segments_df,
    x="segment",
    y="users",
    text="users",
    color="segment",
    color_discrete_map=segment_colors
)

fig.update_traces(
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
    xaxis_title="Segmento",
    yaxis_title="Usuarios",
    showlegend=False,
    margin=dict(l=20, r=20, t=30, b=20)
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# ----------------------------
# Tabla
# ----------------------------

henry_tag("Detalle")

st.subheader("📋 Información de los segmentos")

table = segments_df.rename(
    columns={
        "segment": "Segmento",
        "users": "Usuarios",
        "percentage": "%",
        "strategy": "Modelo recomendado"
    }
)

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ----------------------------
# Explicación
# ----------------------------

henry_tag("Interpretación")

st.markdown(
    """
### 🧠 ¿Por qué segmentamos?

En lugar de recomendar lo mismo a todos los usuarios,
el sistema identifica el comportamiento de compra y selecciona
la estrategia más adecuada.

- 🟢 **Nuevo** → Popularity Model (Cold Start)
- 🔵 **Ocasional** → Item-Item Collaborative Filtering
- 🟡 **Frecuente** → Market Basket Analysis
- 🔴 **Leal** → Reorder Prediction

Este enfoque permite personalizar las recomendaciones
según el nivel de actividad de cada usuario.
"""
)
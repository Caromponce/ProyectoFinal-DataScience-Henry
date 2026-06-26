# importar librerías
import streamlit as st
import pandas as pd

# importar cliente de recomendaciones
from src.api_client import get_recommendations
from src.styles import inject_css


st.set_page_config(
    page_title="Recomendador",
    page_icon="🔍",
    layout="wide"
)

inject_css()

with st.sidebar:
    st.image("assets/logo_data_horizon.png", width=150)

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
    
st.title("🔍 Recomendador de Productos")

st.markdown(
    """
    Ingresá un `user_id` para simular el flujo completo del sistema:
    segmentación del usuario, selección de estrategia y generación de recomendaciones.
    """
)

st.divider()

col_input, col_info = st.columns([1, 2])

with col_input:
    st.subheader("👤 Usuario")

    user_id = st.number_input(
        "User ID",
        min_value=1,
        value=123,
        step=1
    )

    n = st.slider(
        "Cantidad de recomendaciones",
        min_value=1,
        max_value=5,
        value=5
    )

    generate = st.button("🚀 Generar", use_container_width=True)

with col_info:
    st.subheader("🧠 Lógica del sistema")

    st.markdown(
        """
        El sistema identifica el segmento del usuario y selecciona
        automáticamente la mejor estrategia de recomendación:

        - **Usuario Nuevo** → Popularity Model
        - **Usuario Ocasional** → Item-Item Collaborative Filtering
        - **Usuario Frecuente** → Market Basket Analysis
        - **Usuario Leal** → Reorder Prediction
        """
    )

if generate:

    response = get_recommendations(user_id=user_id, n=n)

    strategy_display = {
        "popularity": "Popularity",
        "item_item_cf": "Item-Item CF",
        "market_basket": "Market Basket",
        "reorder_prediction": "Reorder"
    }

    st.divider()

    st.subheader("📌 Resultado de la recomendación")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="👥 Segmento",
            value=response["segment"]
        )

    with col2:
        st.metric(
            label="🧠 Estrategia",
            value=strategy_display[response["strategy"]]
        )

    with col3:
        st.metric(
            label="🆔 Usuario",
            value=response["user_id"]
        )

    st.info(f"🎯 Objetivo: {response['objective']}")

    recommendations_df = pd.DataFrame(response["recommendations"])
    recommendations_df["score"] = recommendations_df["score"].round(2)

    st.subheader("⭐ Productos recomendados")

    st.dataframe(
        recommendations_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("📝 Explicación")

    st.markdown(
        f"""
        El usuario **{response["user_id"]}** fue clasificado como **{response["segment"]}**.

        Por ese motivo, el sistema seleccionó la estrategia
        **{response["strategy_name"]}**, cuyo objetivo es:

        **{response["objective"]}**
        """
    )
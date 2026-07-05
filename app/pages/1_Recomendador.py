# importar librerías
import streamlit as st
import pandas as pd
import requests

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
        <p>Transformamos datos<br>en decisiones</p>
        """,
        unsafe_allow_html=True
    )
    st.divider()

st.title("🔍 Recomendador de Productos")

st.markdown(
    """
    Ingresá un `user_id` y, opcionalmente, productos del carrito para simular
    el flujo completo: segmentación, selección de estrategia y recomendaciones.
    """
)

st.divider()

col_input, col_info = st.columns([1, 2])

with col_input:
    st.subheader("👤 Usuario")

    user_id = st.number_input("User ID", min_value=1, value=1, step=1)

    product_ids_text = st.text_input(
        "Product IDs",
        value="21903, 47209",
        help="Ingresá IDs separados por coma. Ejemplo: 21903, 47209"
    )

    n = st.slider(
        "Cantidad de recomendaciones",
        min_value=1,
        max_value=10,
        value=10
    )

    generate = st.button("🚀 Generar", use_container_width=True)

with col_info:
    st.subheader("🧠 Lógica del sistema")

    st.markdown(
        """
        La API identifica el segmento del usuario y selecciona automáticamente
        la estrategia más adecuada:

        - **Clientes sin historial** → Popularity Model
        - **Clientes Ocasionales** → Item-Item Collaborative Filtering
        - **Clientes de canasta grande** → Market Basket Analysis
        - **Clientes Leales o frecuentes** → Reorder Prediction
        """
    )

if generate:
    try:
        product_ids = [
            int(product_id.strip())
            for product_id in product_ids_text.split(",")
            if product_id.strip()
        ]

        response = get_recommendations(
            user_id=user_id,
            product_ids=product_ids,
            n=n
        )

        result = response.get("result", {})
        recommendations = result.get("recommendations", [])

        strategy_display = {
            "popularity": "Popularity",
            "item_item_cf": "Item-Item CF",
            "market_basket": "Market Basket",
            "market_basket_products": "Market Basket",
            "reorder_prediction": "Reorder"
        }

        st.divider()
        st.subheader("📌 Resultado de la recomendación")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("👥 Segmento", response.get("segment", "Sin dato"))

        with col2:
            st.metric(
                "🧠 Estrategia",
                strategy_display.get(response.get("strategy"), response.get("strategy", "Sin dato"))
            )

        with col3:
            st.metric("🆔 Usuario", response.get("user_id", user_id))

        st.info(f"🎯 Objetivo: {response.get('objective', 'Sin objetivo disponible')}")

        if recommendations:
            recommendations_df = pd.DataFrame(recommendations)

            st.subheader("⭐ Productos recomendados")
            st.dataframe(
                recommendations_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("La API respondió correctamente, pero no devolvió recomendaciones.")

        st.subheader("📝 Explicación")

        st.markdown(
            f"""
            El usuario **{response.get("user_id", user_id)}** fue clasificado como
            **{response.get("segment", "Sin segmento")}**.

            Por ese motivo, el sistema seleccionó la estrategia
            **{response.get("strategy_name", "Sin estrategia")}**, cuyo objetivo es:

            **{response.get("objective", "Sin objetivo disponible")}**
            """
        )

    except ValueError:
        st.error("Revisá los Product IDs. Deben ser números separados por coma.")

    except requests.exceptions.ConnectionError:
        st.error(
            "No se pudo conectar con la API. Verificá que FastAPI esté corriendo en http://127.0.0.1:8000"
        )

    except requests.exceptions.RequestException as error:
        st.error(f"Error al consultar la API: {error}")
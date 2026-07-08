# importar librerías
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# importar cliente de recomendaciones
from src.api_client import get_recommendations
from src.styles import inject_css


st.set_page_config(
    page_title="Recomendador",
    page_icon="🔍",
    layout="wide"
)

inject_css()

BASE_DIR = Path(__file__).resolve().parents[2]
USER_SEGMENTS_PATH = BASE_DIR / "data" / "processed" / "user_segments.csv"


@st.cache_data
def load_user_segments():
    if not USER_SEGMENTS_PATH.exists():
        return pd.DataFrame(columns=["user_id", "segment"])

    users = pd.read_csv(USER_SEGMENTS_PATH)
    users = users[["user_id", "segment"]].dropna()
    users["user_id"] = users["user_id"].astype(int)
    users["segment"] = users["segment"].astype(str)

    return users


def get_client_segment(user_id, user_segments):
    if user_segments.empty:
        return None

    match = user_segments[user_segments["user_id"] == int(user_id)]

    if match.empty:
        return None

    return match.iloc[0]["segment"]


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
    Simulá el flujo principal del sistema: identificación del tipo de cliente,
    selección automática de estrategia y generación de recomendaciones.
    """
)

st.info(
    """
    **Nota:** Market Basket Analysis se explora en su propia sección, porque depende
    del contenido del carrito y no del segmento del cliente.
    """
)

st.divider()

user_segments = load_user_segments()

# Productos válidos para demo de Item-Item CF y Reorder Prediction
DEMO_PRODUCTS = {
    "Banana": 24852,
    "Bag of Organic Bananas": 13176,
    "Organic Strawberries": 21137,
    "Organic Baby Spinach": 21903,
    "Organic Hass Avocado": 47209,
    "Organic Garlic": 24964,
}

col_input, col_info = st.columns([1, 2])

with col_input:
    st.subheader("👤 Tipo de cliente")

    client_type = st.radio(
        "Seleccioná el escenario",
        options=["Cliente nuevo", "Cliente existente"],
        horizontal=False,
        key="client_type_radio"
    )

    detected_segment = None
    selected_products = []
    product_ids = []

    if client_type == "Cliente nuevo":
        st.success("Cliente nuevo / sin historial")
        st.caption("Se utilizará Popularity Baseline.")
        user_id = 999999999

    else:
        st.subheader("🔎 Cliente existente")

        user_id = st.number_input(
            "Número de cliente",
            min_value=1,
            value=66356,
            step=1,
            help="Ingresá un user_id existente dentro del dataset."
        )

        detected_segment = get_client_segment(user_id, user_segments)

        if detected_segment is None:
            st.error(
                "Ese número de cliente no está disponible en user_segments.csv. "
                "Probá con un cliente existente."
            )

            if not user_segments.empty:
                ejemplos = user_segments["user_id"].head(10).tolist()
                st.caption(f"Ejemplos disponibles: {', '.join(map(str, ejemplos))}")

        else:
            st.success(f"Segmento detectado: **{detected_segment}**")

            if detected_segment == "Clientes sin historial de compras":
                st.markdown("**Modelo seleccionado:** Popularity Baseline")
                st.caption("Aunque sea un cliente existente, no tiene historial suficiente. Se usa baseline.")

            elif detected_segment == "Clientes Ocasionales":
                st.markdown("**Modelo seleccionado:** Item-Item Collaborative Filtering")

                selected_products = st.multiselect(
                    "Seleccioná productos válidos de referencia",
                    options=list(DEMO_PRODUCTS.keys()),
                    default=["Organic Strawberries"],
                    help="Estos productos se usan como entrada para buscar productos similares."
                )

                product_ids = [DEMO_PRODUCTS[p] for p in selected_products]

            elif detected_segment == "Clientes Leales o frecuentes":
                st.markdown("**Modelo seleccionado:** Reorder Prediction")

                selected_products = st.multiselect(
                    "Seleccioná productos candidatos a recompra",
                    options=list(DEMO_PRODUCTS.keys()),
                    default=["Banana", "Bag of Organic Bananas", "Organic Strawberries"],
                    help="Reorder Prediction predice si el cliente volvería a comprar estos productos."
                )

                product_ids = [DEMO_PRODUCTS[p] for p in selected_products]

            elif detected_segment == "Clientes de canasta grande":
                st.markdown("**Modelo seleccionado:** Market Basket Analysis")
                st.warning(
                    "Este segmento se trabaja en la sección Market Basket, no en el recomendador individual."
                )

            else:
                st.markdown("**Modelo seleccionado:** Popularity Baseline")
                st.caption("Segmento no reconocido. Se usará fallback seguro.")

    n = st.slider(
        "Cantidad de recomendaciones",
        min_value=1,
        max_value=10,
        value=5
    )

    generate = st.button("🚀 Generar recomendación", use_container_width=True)

with col_info:
    st.subheader("🧠 Lógica del sistema")

    st.markdown(
        """
        El recomendador principal funciona como un **router híbrido**:

        - **Cliente nuevo / sin historial** → Popularity Baseline
        - **Cliente ocasional** → Item-Item Collaborative Filtering
        - **Cliente leal o frecuente** → Reorder Prediction

        Market Basket Analysis se trabaja como módulo complementario en la sección
        específica de carrito y reglas de asociación.
        """
    )


if generate:
    if client_type == "Cliente existente" and detected_segment is None:
        st.warning("Seleccioná un número de cliente válido antes de generar recomendaciones.")

    else:
        try:
            response = get_recommendations(
                user_id=int(user_id),
                product_ids=product_ids,
                n=n
            )

            result = response.get("result", {})
            recommendations = result.get("recommendations", [])
            predictions = result.get("predictions", [])
            message = result.get("message")

            strategy_display = {
                "popularity": "Popularity Baseline",
                "item_item_cf": "Item-Item Collaborative Filtering",
                "market_basket": "Market Basket Analysis",
                "market_basket_products": "Market Basket Analysis",
                "reorder_prediction": "Reorder Prediction"
            }

            st.divider()
            st.subheader("📌 Resultado de la recomendación")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Segmento**")
                st.success(response.get("segment", detected_segment or "Cliente nuevo"))

            with col2:
                st.markdown("**Estrategia**")
                st.info(
                    strategy_display.get(
                        response.get("strategy"),
                        response.get("strategy", "Sin dato")
                    )
                )

            with col3:
                st.markdown("**Cliente**")
                if client_type == "Cliente nuevo":
                    st.warning("Nuevo")
                else:
                    st.info(str(response.get("user_id", user_id)))

            st.info(
                f"🎯 **Objetivo:** {response.get('objective', 'Sin objetivo disponible')}"
            )

            if selected_products:
                st.subheader("🛒 Productos seleccionados")

                st.dataframe(
                    pd.DataFrame(
                        [
                         {
                            "product_id": DEMO_PRODUCTS[name],
                            "product_name": name
                        }
                        for name in selected_products
                        ]
                    ),
                    use_container_width=True,
                    hide_index=True
                )

            if recommendations:
                recommendations_df = pd.DataFrame(recommendations)

                st.subheader("⭐ Productos recomendados")
                st.dataframe(
                    recommendations_df,
                    use_container_width=True,
                    hide_index=True
                )

            elif predictions:
                predictions_df = pd.DataFrame(predictions)

                st.subheader("🔁 Predicción de recompra")
                st.dataframe(
                    predictions_df,
                    use_container_width=True,
                    hide_index=True
                )

            elif message:
                st.warning(message)

            else:
                st.warning(
                    "La API respondió correctamente, pero no devolvió recomendaciones."
                )

            st.subheader("📝 Explicación")

            if client_type == "Cliente nuevo":
                st.markdown(
                    """
                    Se simuló un **cliente nuevo o sin historial**.  
                    Por eso el sistema utiliza recomendaciones basadas en popularidad.
                    """
                )

            elif detected_segment == "Clientes Ocasionales":
                st.markdown(
                    f"""
                    El cliente **{user_id}** pertenece al segmento **Clientes Ocasionales**.  
                    Para este perfil se utiliza **Item-Item Collaborative Filtering**, tomando
como referencia     los productos seleccionados: **{", ".join(selected_products)}**.
                    """
                )

            else:
                st.markdown(
                    f"""
                    El cliente **{user_id}** pertenece al segmento **{detected_segment}**.  
                    Para este perfil se utiliza **Reorder Prediction**, priorizando productos
                    con mayor probabilidad de recompra según su historial.
                    """
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "No se pudo conectar con la API. En Render debería usar la URL configurada en API_URL."
            )

        except requests.exceptions.RequestException as error:
            st.error(f"Error al consultar la API: {error}")

        except Exception as error:
            st.error("Ocurrió un error al generar la recomendación.")
            st.code(str(error))
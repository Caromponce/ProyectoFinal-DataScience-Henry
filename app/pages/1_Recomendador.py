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

# Productos validados para demo del modelo Item-Item CF
DEMO_PRODUCTS = {
    "Organic Strawberries": 21137,
    "Organic Garlic": 24964,
    "Organic Hass Avocado": 47209,
    "Organic Baby Spinach": 21903,
    "Banana": 24852,
    "Bag of Organic Bananas": 13176,
}

col_input, col_info = st.columns([1, 2])

with col_input:
    st.subheader("👤 Tipo de cliente")

    client_type = st.radio(
        "Seleccioná el escenario",
        options=["Cliente nuevo", "Cliente existente"],
        horizontal=False
    )

    detected_segment = None
    selected_product_id = None
    selected_product_name = None
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
            value=3,
            step=1,
            help="Ingresá un cliente existente dentro del dataset."
        )

        detected_segment = get_client_segment(user_id, user_segments)

        if detected_segment is None:
            st.error(
                "Ese número de cliente no está disponible en user_segments.csv. "
                "Probá con un cliente existente."
            )

            if not user_segments.empty:
                ejemplos = user_segments["user_id"].head(10).tolist()
                st.caption(
                    f"Ejemplos disponibles: {', '.join(map(str, ejemplos))}"
                )

        else:
            st.success(f"Segmento detectado: **{detected_segment}**")

            if detected_segment == "Clientes Ocasionales":
                st.markdown("**Modelo seleccionado:** Item-Item Collaborative Filtering")

                selected_product_name = st.selectbox(
                    "Producto de referencia",
                    options=list(DEMO_PRODUCTS.keys()),
                    help="Productos validados para demostrar recomendaciones Item-Item."
                )

                selected_product_id = DEMO_PRODUCTS[selected_product_name]
                product_ids = [selected_product_id]

            elif detected_segment in ["Clientes Leales", "Clientes Leales o frecuentes"]:
                st.markdown("**Modelo seleccionado:** Reorder Prediction")
                st.caption(
                    "Para clientes leales, el sistema recomienda según historial de recompra. "
                    "No requiere seleccionar producto manualmente."
                )
                product_ids = []

            else:
                st.markdown("**Modelo seleccionado:** estrategia definida por la API")
                product_ids = []

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

            if selected_product_id is not None:
                st.subheader("🛒 Producto utilizado como referencia")

                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "product_id": selected_product_id,
                                "product_name": selected_product_name
                            }
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
                    como referencia el producto seleccionado: **{selected_product_name}**.
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
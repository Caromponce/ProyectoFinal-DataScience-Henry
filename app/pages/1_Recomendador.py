# importar librerías
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# importar cliente de recomendaciones
from src.api_client import get_recommendations
from src.styles import inject_css
from src.mba_prod_recommender import MBA_Prod_Recommender


st.set_page_config(
    page_title="Recomendador",
    page_icon="🔍",
    layout="wide"
)

inject_css()

BASE_DIR = Path(__file__).resolve().parents[2]
PRODUCTS_CATALOG_PATH = BASE_DIR / "data" / "processed" / "products_catalog.csv"
USER_SEGMENTS_PATH = BASE_DIR / "data" / "processed" / "user_segments.csv"


@st.cache_data
def load_products_catalog():
    if not PRODUCTS_CATALOG_PATH.exists():
        return pd.DataFrame(columns=["product_id", "product_name"])

    products = pd.read_csv(PRODUCTS_CATALOG_PATH)
    products = products[["product_id", "product_name"]].dropna()
    products["product_id"] = products["product_id"].astype(int)
    products["product_name"] = products["product_name"].astype(str)

    return products.sort_values("product_name")


@st.cache_data
def load_user_segments():
    if not USER_SEGMENTS_PATH.exists():
        return pd.DataFrame(columns=["user_id", "segment"])

    users = pd.read_csv(USER_SEGMENTS_PATH)
    users = users[["user_id", "segment"]].dropna()
    users["user_id"] = users["user_id"].astype(int)
    users["segment"] = users["segment"].astype(str)

    return users


@st.cache_resource
def load_mba_product_model():
    return MBA_Prod_Recommender.load()


@st.cache_data
def get_valid_products_from_mba():
    """
    Devuelve solo productos que aparecen como antecedente en reglas MBA.
    Esto evita mostrar miles de productos sin recomendación disponible.
    """
    try:
        model = load_mba_product_model()

        product_ids = set()

        for antecedents in model.rules["antecedents"]:
            product_ids.update(list(antecedents))

        products = [
            {
                "product_id": int(product_id),
                "product_name": model.id_to_name.get(
                    product_id,
                    f"Producto {product_id}"
                )
            }
            for product_id in product_ids
        ]

        return pd.DataFrame(products).sort_values("product_name")

    except Exception:
        return pd.DataFrame(columns=["product_id", "product_name"])


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
    Simulá el flujo completo del sistema: identificación del tipo de cliente,
    selección automática de estrategia y generación de recomendaciones.
    """
)

st.divider()

products_catalog = load_products_catalog()
valid_products = get_valid_products_from_mba()
user_segments = load_user_segments()

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

    if client_type == "Cliente nuevo":
        st.info(
            """
            Para clientes sin historial, el sistema utiliza recomendaciones
            basadas en popularidad.
            """
        )

        user_id = 999999999

    else:
        user_id = st.number_input(
            "Número de cliente",
            min_value=1,
            value=3,
            step=1,
            help="Ingresá el número de cliente existente."
        )

        detected_segment = get_client_segment(user_id, user_segments)

        if detected_segment:
            st.success(f"Cliente encontrado: **{detected_segment}**")
        else:
            st.warning(
                "No se encontró el cliente en user_segments.csv. "
                "La API intentará clasificarlo igualmente."
            )

        st.subheader("🛒 Producto de referencia")

        if not valid_products.empty:
            product_options = valid_products["product_name"].tolist()

            selected_product_name = st.selectbox(
                "Seleccioná un producto con reglas disponibles",
                options=product_options,
                help="Se muestran solo productos que forman parte de reglas de asociación."
            )

            product_name_to_id = dict(
                zip(
                    valid_products["product_name"],
                    valid_products["product_id"]
                )
            )

            selected_product_id = int(product_name_to_id[selected_product_name])

            st.caption(
                "La interfaz muestra el nombre del producto, pero la API recibe internamente el product_id."
            )

        elif not products_catalog.empty:
            st.warning(
                "No se pudieron cargar las reglas MBA. "
                "Se muestra el catálogo general como respaldo."
            )

            product_options = products_catalog["product_name"].tolist()

            selected_product_name = st.selectbox(
                "Seleccioná un producto",
                options=product_options
            )

            product_name_to_id = dict(
                zip(
                    products_catalog["product_name"],
                    products_catalog["product_id"]
                )
            )

            selected_product_id = int(product_name_to_id[selected_product_name])

        else:
            st.warning(
                "No se encontró catálogo de productos. "
                "Se habilita ingreso manual de ID."
            )

            selected_product_id = st.number_input(
                "Product ID",
                min_value=1,
                value=21903,
                step=1
            )

            selected_product_name = f"Producto {selected_product_id}"

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
        La API identifica el segmento del cliente y selecciona automáticamente
        la estrategia más adecuada:

        - **Clientes sin historial** → Popularity Baseline
        - **Clientes Ocasionales** → Item-Item Collaborative Filtering
        - **Clientes de canasta grande** → Market Basket Analysis
        - **Clientes Leales o frecuentes** → Reorder Prediction
        """
    )

    st.info(
        """
        Para evitar recomendaciones vacías durante la demo, el selector muestra
        productos que forman parte de reglas reales de asociación.
        """
    )


if generate:
    try:
        if client_type == "Cliente nuevo":
            product_ids = []
        else:
            product_ids = [int(selected_product_id)]

        response = get_recommendations(
            user_id=int(user_id),
            product_ids=product_ids,
            n=n
        )

        result = response.get("result", {})
        recommendations = result.get("recommendations", [])

        strategy_display = {
            "popularity": "Popularity Baseline",
            "item_item_cf": "Item-Item CF",
            "market_basket": "Market Basket",
            "market_basket_products": "Market Basket",
            "reorder_prediction": "Reorder Prediction"
        }

        st.divider()
        st.subheader("📌 Resultado de la recomendación")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Segmento**")
            st.success(response.get("segment", detected_segment or "Sin dato"))

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

        if client_type == "Cliente existente":
            selected_df = pd.DataFrame(
                [
                    {
                        "product_id": selected_product_id,
                        "product_name": selected_product_name
                    }
                ]
            )

            st.subheader("🛒 Producto utilizado como entrada")
            st.dataframe(
                selected_df,
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
                f"""
                Se simuló un **cliente nuevo o sin historial de compras**.

                Por ese motivo, el sistema seleccionó la estrategia
                **{response.get("strategy_name", "Sin estrategia")}**, cuyo objetivo es:

                **{response.get("objective", "Sin objetivo disponible")}**
                """
            )
        else:
            st.markdown(
                f"""
                El cliente **{response.get("user_id", user_id)}** pertenece al segmento
                **{response.get("segment", detected_segment or "Sin segmento")}**.

                A partir del producto de referencia **{selected_product_name}**, el sistema
                seleccionó la estrategia **{response.get("strategy_name", "Sin estrategia")}**.

                **Objetivo:** {response.get("objective", "Sin objetivo disponible")}
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
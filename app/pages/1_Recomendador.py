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
PRODUCTS_CATALOG_PATH = BASE_DIR / "data" / "processed" / "products_catalog.csv"


@st.cache_data
def load_products_catalog():
    """
    Carga el catálogo de productos con product_id y product_name.
    """
    if not PRODUCTS_CATALOG_PATH.exists():
        return pd.DataFrame(columns=["product_id", "product_name"])

    products = pd.read_csv(PRODUCTS_CATALOG_PATH)

    products = products[["product_id", "product_name"]].dropna()
    products["product_id"] = products["product_id"].astype(int)
    products["product_name"] = products["product_name"].astype(str)

    return products.sort_values("product_name")


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

col_input, col_info = st.columns([1, 2])

with col_input:
    st.subheader("👤 Tipo de cliente")

    client_type = st.radio(
        "Seleccioná el escenario",
        options=["Cliente nuevo", "Cliente existente"],
        horizontal=False
    )

    if client_type == "Cliente nuevo":
        st.info(
            """
            Para clientes sin historial, el sistema utiliza recomendaciones
            basadas en popularidad.
            """
        )
        user_id = 999999999
        selected_products = []

    else:
        user_id = st.number_input(
            "Número de cliente",
            min_value=1,
            value=1,
            step=1,
            help="Ingresá el número de cliente existente."
        )

        st.subheader("🛒 Productos del carrito")

        if products_catalog.empty:
            st.warning(
                "No se encontró data/processed/products_catalog.csv. "
                "Se usará el ingreso manual de IDs."
            )

            product_ids_text = st.text_input(
                "Product IDs",
                value="21903, 47209",
                help="Ingresá IDs separados por coma. Ejemplo: 21903, 47209"
            )

            selected_products = []

        else:
            product_options = products_catalog["product_name"].tolist()

            default_products = [
                product_name
                for product_name in ["Organic Strawberries", "Organic Garlic"]
                if product_name in product_options
            ]

            selected_products = st.multiselect(
                "Seleccioná productos comprados",
                options=product_options,
                default=default_products,
                help="Buscá productos por nombre. Internamente se envían sus product_id a la API."
            )

    n = st.slider(
        "Cantidad de recomendaciones",
        min_value=1,
        max_value=10,
        value=10
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
        La interfaz muestra nombres de productos para mejorar la experiencia
        del usuario, pero la API sigue trabajando internamente con `product_id`.
        """
    )


if generate:
    try:
        if client_type == "Cliente nuevo":
            product_ids = []

        elif products_catalog.empty:
            product_ids = [
                int(product_id.strip())
                for product_id in product_ids_text.split(",")
                if product_id.strip()
            ]

        else:
            product_name_to_id = dict(
                zip(
                    products_catalog["product_name"],
                    products_catalog["product_id"]
                )
            )

            product_ids = [
                int(product_name_to_id[product_name])
                for product_name in selected_products
            ]

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
            st.metric("👥 Segmento", response.get("segment", "Sin dato"))

        with col2:
            st.metric(
                "🧠 Estrategia",
                strategy_display.get(
                    response.get("strategy"),
                    response.get("strategy", "Sin dato")
                )
            )

        with col3:
            if client_type == "Cliente nuevo":
                st.metric("🆔 Cliente", "Nuevo")
            else:
                st.metric("🆔 Cliente", response.get("user_id", user_id))

        st.info(
            f"🎯 Objetivo: {response.get('objective', 'Sin objetivo disponible')}"
        )

        if client_type == "Cliente existente" and product_ids:
            selected_df = pd.DataFrame(
                {
                    "product_id": product_ids,
                    "product_name": selected_products
                    if not products_catalog.empty
                    else product_ids
                }
            )

            st.subheader("🛒 Productos utilizados como entrada")
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
                El cliente **{response.get("user_id", user_id)}** fue clasificado como
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
            "No se pudo conectar con la API. En Render debería usar la URL configurada en API_URL."
        )

    except requests.exceptions.RequestException as error:
        st.error(f"Error al consultar la API: {error}")
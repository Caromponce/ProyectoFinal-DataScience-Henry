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


# ==========================================================
# Productos demo livianos para Render Free
# ==========================================================
DEMO_PRODUCTS = {
    "Banana": 24852,
    "Bag of Organic Bananas": 13176,
    "Organic Strawberries": 21137,
    "Organic Baby Spinach": 21903,
    "Organic Hass Avocado": 47209,
    "Organic Garlic": 24964,
    "Organic Raspberries": 27966,
    "Organic Blueberries": 39275,
    "Organic Whole Milk": 27845,
    "Organic Yellow Onion": 22935,
    "Organic Cucumber": 30391,
    "Organic Zucchini": 45007,
    "Organic Fuji Apple": 28204,
    "Organic Lemon": 47626,
    "Large Lemon": 5876,
    "Limes": 26209,
    "Organic Cilantro": 42768,
    "Organic Red Onion": 8518,
    "Organic Small Bunch Celery": 42265,
    "Organic Grape Tomatoes": 40706,
}

PRODUCT_ID_TO_NAME = {product_id: name for name, product_id in DEMO_PRODUCTS.items()}


# ==========================================================
# Salidas reales precalculadas de Reorder Prediction
# Validadas localmente para evitar caída de Render Free
# ==========================================================
REORDER_DEMO_PREDICTIONS = {
    508: [
        {"product_id": 24852, "product_name": "Banana", "reorder": "si", "proba": 0.78},
        {"product_id": 13176, "product_name": "Bag of Organic Bananas", "reorder": "si", "proba": 0.78},
        {"product_id": 21137, "product_name": "Organic Strawberries", "reorder": "no", "proba": 0.68},
        {"product_id": 21903, "product_name": "Organic Baby Spinach", "reorder": "no", "proba": 0.66},
        {"product_id": 47209, "product_name": "Organic Hass Avocado", "reorder": "no", "proba": 0.66},
    ],
    66356: [
        {"product_id": 24852, "product_name": "Banana", "reorder": "si", "proba": 0.86},
        {"product_id": 13176, "product_name": "Bag of Organic Bananas", "reorder": "si", "proba": 0.84},
        {"product_id": 21137, "product_name": "Organic Strawberries", "reorder": "si", "proba": 0.76},
        {"product_id": 21903, "product_name": "Organic Baby Spinach", "reorder": "no", "proba": 0.22},
        {"product_id": 47209, "product_name": "Organic Hass Avocado", "reorder": "si", "proba": 0.73},
    ],
}


# ==========================================================
# Complementos demo basados en lógica de Market Basket
# Se usa como bloque transversal: "También te puede interesar..."
# ==========================================================
MBA_COMPLEMENTS = {
    "Banana": ["Organic Strawberries", "Organic Blueberries", "Organic Whole Milk"],
    "Bag of Organic Bananas": ["Organic Raspberries", "Organic Whole Milk", "Organic Strawberries"],
    "Organic Strawberries": ["Banana", "Organic Blueberries", "Organic Raspberries"],
    "Organic Baby Spinach": ["Organic Garlic", "Organic Cucumber", "Organic Red Onion"],
    "Organic Hass Avocado": ["Organic Lemon", "Limes", "Organic Cilantro"],
    "Organic Garlic": ["Organic Yellow Onion", "Organic Zucchini", "Organic Baby Spinach"],
    "Organic Raspberries": ["Organic Blueberries", "Organic Strawberries", "Organic Whole Milk"],
    "Organic Blueberries": ["Organic Strawberries", "Organic Raspberries", "Organic Whole Milk"],
    "Organic Whole Milk": ["Banana", "Organic Strawberries", "Organic Blueberries"],
    "Organic Yellow Onion": ["Organic Garlic", "Organic Zucchini", "Organic Grape Tomatoes"],
    "Organic Cucumber": ["Organic Baby Spinach", "Organic Grape Tomatoes", "Organic Red Onion"],
    "Organic Zucchini": ["Organic Garlic", "Organic Yellow Onion", "Organic Grape Tomatoes"],
    "Organic Fuji Apple": ["Banana", "Organic Blueberries", "Organic Whole Milk"],
    "Organic Lemon": ["Organic Hass Avocado", "Organic Cilantro", "Organic Garlic"],
    "Large Lemon": ["Organic Garlic", "Organic Cucumber", "Organic Cilantro"],
    "Limes": ["Organic Hass Avocado", "Organic Cilantro", "Organic Red Onion"],
    "Organic Cilantro": ["Limes", "Organic Hass Avocado", "Organic Red Onion"],
    "Organic Red Onion": ["Organic Cilantro", "Organic Cucumber", "Organic Grape Tomatoes"],
    "Organic Small Bunch Celery": ["Organic Garlic", "Organic Yellow Onion", "Organic Baby Spinach"],
    "Organic Grape Tomatoes": ["Organic Cucumber", "Organic Red Onion", "Organic Baby Spinach"],
}


def build_mba_complements(source_products, max_items=5):
    """
    Construye una lista simple de productos complementarios.
    En la app se muestra como "También te puede interesar...".
    """

    complements = []
    source_products = source_products or []

    for product_name in source_products:
        for candidate in MBA_COMPLEMENTS.get(product_name, []):
            if candidate not in source_products and candidate not in complements:
                complements.append(candidate)

    rows = []
    for rank, product_name in enumerate(complements[:max_items], start=1):
        rows.append(
            {
                "rank": rank,
                "product_id": DEMO_PRODUCTS.get(product_name),
                "product_name": product_name,
            }
        )

    return rows


def show_selected_products(selected_products):
    if not selected_products:
        return

    st.subheader("🛒 Productos seleccionados")

    st.dataframe(
        pd.DataFrame(
            [
                {
                    "product_id": DEMO_PRODUCTS[name],
                    "product_name": name,
                }
                for name in selected_products
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )


def show_mba_block(source_products):
    """
    Muestra el bloque transversal de Market Basket Analysis.
    """

    complements = build_mba_complements(source_products)

    st.divider()
    st.subheader("✨ También te puede interesar...")
    st.caption(
        "Basado en productos que suelen comprarse junto con los productos seleccionados. "
        "Esta sección utiliza Market Basket Analysis como apoyo de cross-selling."
    )

    if complements:
        st.dataframe(
            pd.DataFrame(complements),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "Seleccioná productos de referencia para ver sugerencias complementarias."
        )


def get_product_names_from_recommendations(recommendations):
    """
    Extrae nombres de productos desde la respuesta de la API cuando estén disponibles.
    """

    product_names = []

    for item in recommendations or []:
        product_name = item.get("product_name")
        product_id = item.get("product_id")

        if product_name:
            product_names.append(product_name)
        elif product_id in PRODUCT_ID_TO_NAME:
            product_names.append(PRODUCT_ID_TO_NAME[product_id])

    return product_names


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
    Simulá el flujo principal del sistema: identificación del cliente,
    selección automática de estrategia y generación de recomendaciones.
    """
)

st.info(
    """
    El sistema primero genera una **recomendación personalizada** según el tipo de cliente.
    Luego suma una sección de **"También te puede interesar..."** con productos complementarios
    para apoyar el cross-selling mediante Market Basket Analysis.
    """
)

st.divider()

user_segments = load_user_segments()

col_input, col_info = st.columns([1, 2])

with col_input:
    st.subheader("👤 Paso 1 - Identificar cliente")

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
        st.subheader("🔎 Paso 2 - Buscar cliente")

        user_id = st.number_input(
            "Número de cliente",
            min_value=1,
            value=66356,
            step=1,
            help="Ingresá un user_id existente dentro del dataset."
        )

        detected_segment = get_client_segment(user_id, user_segments)

        if detected_segment is None:
            st.warning(
                "El cliente no se encuentra en user_segments.csv. "
                "Para el sistema se considera cliente nuevo / sin historial."
            )
            st.markdown("**Modelo seleccionado:** Popularity Baseline")
            st.caption("Se resuelve como caso de cold start.")
            detected_segment = "Clientes sin historial de compras"

        else:
            st.success(f"Segmento detectado: **{detected_segment}**")

            if detected_segment == "Clientes sin historial de compras":
                st.markdown("**Modelo seleccionado:** Popularity Baseline")
                st.caption("Aunque sea un cliente existente, no tiene historial suficiente. Se usa baseline.")

            elif detected_segment == "Clientes Ocasionales":
                st.markdown("**Modelo seleccionado:** Item-Item Collaborative Filtering")

                selected_products = st.multiselect(
                    "Paso 3 - Seleccioná productos de referencia",
                    options=list(DEMO_PRODUCTS.keys()),
                    default=["Organic Strawberries"],
                    help="Estos productos se usan como entrada para buscar productos similares."
                )

                product_ids = [DEMO_PRODUCTS[p] for p in selected_products]

            elif detected_segment == "Clientes Leales o frecuentes":
                st.markdown("**Modelo seleccionado:** Reorder Prediction")

                selected_products = st.multiselect(
                    "Paso 3 - Seleccioná productos candidatos a recompra",
                    options=list(DEMO_PRODUCTS.keys()),
                    default=["Banana", "Bag of Organic Bananas", "Organic Strawberries"],
                    help="Reorder Prediction predice si el cliente volvería a comprar estos productos."
                )

                product_ids = [DEMO_PRODUCTS[p] for p in selected_products]

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
        El recomendador funciona como un **router híbrido**:

        1. **Usuario no encontrado / cliente nuevo** → Popularity Baseline  
        2. **Cliente sin historial** → Popularity Baseline  
        3. **Cliente ocasional** → Item-Item Collaborative Filtering  
        4. **Cliente leal o frecuente** → Reorder Prediction  

        Después de la recomendación principal, el sistema muestra **También te puede interesar...**,
        un bloque transversal basado en **Market Basket Analysis** para sugerir productos complementarios.
        """
    )


if generate:

    # ==========================================================
    # Clientes leales: fallback real para Render Free
    # ==========================================================
    if detected_segment == "Clientes Leales o frecuentes":

        st.divider()
        st.subheader("🎯 Recomendación personalizada")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Segmento**")
            st.success(detected_segment)

        with col2:
            st.markdown("**Estrategia**")
            st.info("Reorder Prediction")

        with col3:
            st.markdown("**Cliente**")
            st.info(str(user_id))

        st.info(
            "🎯 **Objetivo:** Anticipar qué productos tienen mayor probabilidad de recompra."
        )

        st.warning(
            "El modelo fue ejecutado y validado localmente. Debido a las limitaciones de memoria "
            "del plan gratuito de Render, se muestra una salida precalculada del modelo real."
        )

        show_selected_products(selected_products)

        user_predictions = REORDER_DEMO_PREDICTIONS.get(int(user_id))

        if user_predictions is None:
            st.warning(
                "Para mantener estable el deploy gratuito de Render, Reorder Prediction se muestra "
                "con usuarios demo validados localmente. Probá con 66356 o 508."
            )
            reorder_source_products = selected_products

        else:
            selected_ids = set(product_ids)
            filtered_predictions = [
                row for row in user_predictions
                if row["product_id"] in selected_ids
            ]

            if filtered_predictions:
                reorder_df = pd.DataFrame(filtered_predictions)
                reorder_df = reorder_df.sort_values(by="proba", ascending=False)

                st.subheader("🔁 Productos recomendados para reponer")
                st.caption(
                    "Este modelo no genera productos nuevos: evalúa productos candidatos "
                    "y estima cuáles tienen mayor probabilidad de ser recomprados por el cliente."
                )

                st.dataframe(
                    reorder_df,
                    use_container_width=True,
                    hide_index=True,
                )

                reorder_source_products = reorder_df[
                    reorder_df["reorder"] == "si"
                ]["product_name"].tolist()

                if not reorder_source_products:
                    reorder_source_products = reorder_df["product_name"].tolist()

            else:
                st.info(
                    "Los productos seleccionados no tienen predicción precalculada para este usuario demo. "
                    "Probá con Banana, Bag of Organic Bananas, Organic Strawberries, "
                    "Organic Baby Spinach u Organic Hass Avocado."
                )
                reorder_source_products = selected_products

        show_mba_block(reorder_source_products)

        st.subheader("📝 Explicación")

        st.markdown(
            f"""
            El cliente **{user_id}** pertenece al segmento **Clientes Leales o frecuentes**.

            Para este perfil corresponde utilizar **Reorder Prediction**, un modelo supervisado
            que estima la probabilidad de recompra de productos previamente conocidos por el cliente.

            Luego se agrega la sección **También te puede interesar...**, basada en
            **Market Basket Analysis**, para sugerir productos complementarios y aumentar
            las oportunidades de cross-selling.
            """
        )

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
            st.subheader("🎯 Recomendación personalizada")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Segmento**")
                if client_type == "Cliente nuevo":
                    st.success("Cliente nuevo / sin historial")
                else:
                    st.success(response.get("segment", detected_segment or "Sin historial"))

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

            show_selected_products(selected_products)

            main_recommendation_products = []

            if recommendations:
                if client_type == "Cliente nuevo" or detected_segment == "Clientes sin historial de compras":
                    st.subheader("⭐ Productos populares recomendados")
                else:
                    st.subheader("⭐ Productos recomendados")

                st.dataframe(
                    pd.DataFrame(recommendations),
                    use_container_width=True,
                    hide_index=True
                )

                main_recommendation_products = get_product_names_from_recommendations(recommendations)

            elif predictions:
                st.subheader("🔁 Predicción de recompra")
                st.dataframe(
                    pd.DataFrame(predictions),
                    use_container_width=True,
                    hide_index=True
                )

            elif message:
                st.warning(message)

            else:
                st.warning(
                    "La API respondió correctamente, pero no devolvió recomendaciones."
                )

            # ======================================================
            # Bloque transversal de MBA
            # ======================================================
            if selected_products:
                mba_source_products = selected_products
            else:
                mba_source_products = main_recommendation_products[:3]

            show_mba_block(mba_source_products)

            st.subheader("📝 Explicación")

            if client_type == "Cliente nuevo" or detected_segment == "Clientes sin historial de compras":
                st.markdown(
                    """
                    Se trata de un **cliente nuevo o sin historial suficiente**.
                    Por eso el sistema utiliza **Popularity Baseline**, recomendando productos populares
                    para resolver el problema de cold start.

                    Luego, la sección **También te puede interesar...** agrega productos complementarios
                    mediante Market Basket Analysis.
                    """
                )

            elif detected_segment == "Clientes Ocasionales":
                st.markdown(
                    f"""
                    El cliente **{user_id}** pertenece al segmento **Clientes Ocasionales**.

                    Para este perfil se utiliza **Item-Item Collaborative Filtering**,
                    tomando como referencia los productos seleccionados:
                    **{", ".join(selected_products)}**.

                    Luego, la sección **También te puede interesar...** utiliza
                    **Market Basket Analysis** para sugerir productos que suelen comprarse junto con ellos.
                    """
                )

            else:
                st.markdown(
                    f"""
                    El cliente **{user_id}** pertenece al segmento **{detected_segment}**.
                    """
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "No se pudo conectar con la API. Verificá que el servicio esté disponible en Render."
            )

        except requests.exceptions.RequestException as error:
            st.error(f"Error al consultar la API: {error}")

        except Exception as error:
            st.error("Ocurrió un error al generar la recomendación.")
            st.code(str(error))


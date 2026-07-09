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
 
 
# Productos válidos para demo de Item-Item CF, Reorder Prediction y MBA complementario
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
    "Organic Avocado": 47766,
    "Organic Baby Arugula": 21616,
    "Organic Baby Carrots": 42265,
    "Organic Broccoli": 9839,
    "Organic Gala Apples": 37646,
    "Organic Honeycrisp Apples": 72,
    "Organic Whole String Cheese": 22035,
    "Organic Large Extra Fancy Fuji Apple": 19057,
    "Organic Granny Smith Apple": 39877,
    "Organic Bartlett Pear": 43122,
    "Organic Red Bell Pepper": 10749,
    "Organic Roma Tomato": 26369,
    "Organic Baby Kale": 35547,
    "Organic Spring Mix": 37687,
    "Asparagus": 46979,
    "Organic Green Seedless Grapes": 38777,
    "Organic Kiwi": 39928,
    "Organic Blackberries": 26604,
    "Organic Half & Half": 49235,
}
 
 
# Reglas demo para la sección "También te puede interesar..."
# Representan recomendaciones complementarias basadas en productos que suelen comprarse juntos.
MBA_COMPLEMENTS = {
    "Banana": [
        "Organic Strawberries",
        "Organic Blueberries",
        "Organic Whole Milk",
        "Organic Raspberries",
        "Organic Fuji Apple",
    ],
    "Bag of Organic Bananas": [
        "Organic Strawberries",
        "Organic Blueberries",
        "Organic Whole Milk",
        "Organic Raspberries",
        "Organic Fuji Apple",
    ],
    "Organic Strawberries": [
        "Banana",
        "Organic Blueberries",
        "Organic Raspberries",
        "Organic Whole Milk",
        "Organic Fuji Apple",
    ],
    "Organic Baby Spinach": [
        "Organic Hass Avocado",
        "Organic Cucumber",
        "Organic Garlic",
        "Organic Grape Tomatoes",
        "Organic Red Onion",
    ],
    "Organic Hass Avocado": [
        "Organic Baby Spinach",
        "Organic Cucumber",
        "Organic Grape Tomatoes",
        "Limes",
        "Organic Cilantro",
    ],
    "Organic Garlic": [
        "Organic Yellow Onion",
        "Organic Zucchini",
        "Organic Baby Spinach",
        "Organic Cucumber",
        "Organic Red Onion",
    ],
    "Organic Raspberries": [
        "Organic Strawberries",
        "Organic Blueberries",
        "Banana",
        "Organic Whole Milk",
        "Organic Fuji Apple",
    ],
    "Organic Blueberries": [
        "Organic Strawberries",
        "Organic Raspberries",
        "Banana",
        "Organic Whole Milk",
        "Organic Fuji Apple",
    ],
    "Organic Whole Milk": [
        "Banana",
        "Organic Strawberries",
        "Organic Blueberries",
        "Organic Raspberries",
        "Bag of Organic Bananas",
    ],
    "Organic Yellow Onion": [
        "Organic Garlic",
        "Organic Zucchini",
        "Organic Baby Spinach",
        "Organic Cucumber",
        "Organic Red Onion",
    ],
    "Organic Cucumber": [
        "Organic Hass Avocado",
        "Organic Baby Spinach",
        "Organic Grape Tomatoes",
        "Organic Red Onion",
        "Organic Cilantro",
    ],
    "Organic Zucchini": [
        "Organic Garlic",
        "Organic Yellow Onion",
        "Organic Baby Spinach",
        "Organic Cucumber",
        "Organic Red Onion",
    ],
    "Organic Fuji Apple": [
        "Banana",
        "Organic Strawberries",
        "Organic Blueberries",
        "Organic Raspberries",
        "Organic Whole Milk",
    ],
    "Organic Lemon": [
        "Organic Garlic",
        "Organic Baby Spinach",
        "Organic Cucumber",
        "Organic Cilantro",
        "Organic Hass Avocado",
    ],
    "Large Lemon": [
        "Organic Garlic",
        "Organic Baby Spinach",
        "Organic Cucumber",
        "Organic Cilantro",
        "Organic Hass Avocado",
    ],
    "Limes": [
        "Organic Hass Avocado",
        "Organic Cilantro",
        "Organic Red Onion",
        "Organic Grape Tomatoes",
        "Organic Cucumber",
    ],
    "Organic Cilantro": [
        "Organic Hass Avocado",
        "Limes",
        "Organic Red Onion",
        "Organic Grape Tomatoes",
        "Organic Cucumber",
    ],
    "Organic Red Onion": [
        "Organic Hass Avocado",
        "Limes",
        "Organic Cilantro",
        "Organic Grape Tomatoes",
        "Organic Cucumber",
    ],
    "Organic Small Bunch Celery": [
        "Organic Garlic",
        "Organic Yellow Onion",
        "Organic Baby Spinach",
        "Organic Cucumber",
        "Organic Zucchini",
    ],
    "Organic Grape Tomatoes": [
        "Organic Hass Avocado",
        "Organic Cucumber",
        "Organic Baby Spinach",
        "Organic Red Onion",
        "Organic Cilantro",
    ],
}
 
 
def build_selected_products_df(selected_products):
    return pd.DataFrame(
        [
            {
                "product_id": DEMO_PRODUCTS[name],
                "product_name": name,
            }
            for name in selected_products
        ]
    )
 
 
def build_mba_complements(selected_products, n=5):
    """
    Construye una tabla liviana de productos complementarios para la demo.

    Primero busca reglas específicas en MBA_COMPLEMENTS.
    Si los productos seleccionados no tienen reglas cargadas, utiliza un fallback
    con productos populares compatibles para que la sección transversal
    "También te puede interesar..." siempre pueda mostrarse en la demo.
    """

    complements = []
    selected_set = set(selected_products)

    for product_name in selected_products:
        for complement in MBA_COMPLEMENTS.get(product_name, []):
            if complement not in selected_set and complement not in complements:
                complements.append(complement)

    fallback_complements = [
        "Banana",
        "Bag of Organic Bananas",
        "Organic Strawberries",
        "Organic Baby Spinach",
        "Organic Hass Avocado",
        "Organic Blueberries",
        "Organic Raspberries",
        "Organic Whole Milk",
        "Organic Cucumber",
        "Organic Garlic",
    ]

    for complement in fallback_complements:
        if len(complements) >= n:
            break

        if complement not in selected_set and complement not in complements:
            complements.append(complement)

    complements = complements[:n]

    return pd.DataFrame(
        [
            {
                "product_id": DEMO_PRODUCTS[name],
                "product_name": name,
                "rank": index + 1,
            }
            for index, name in enumerate(complements)
        ]
    )
 
 
def show_mba_section(selected_products, n=5):
    """
    Muestra la sección transversal de cross-selling.
    Para clientes nuevos o sin productos seleccionados, no se muestra para evitar confusión.
    """
    if not selected_products:
        return
 
    mba_df = build_mba_complements(selected_products, n=n)
 
    if mba_df.empty:
        return
 
    st.divider()
    st.subheader("✨ También te puede interesar...")
    st.caption(
        "Basado en productos que suelen comprarse junto con los productos seleccionados. "
        "Esta sección utiliza Market Basket Analysis como apoyo de cross-selling."
    )
 
    st.dataframe(
        mba_df,
        use_container_width=True,
        hide_index=True,
    )
 
 
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
    **Lógica del sistema:** primero se genera una recomendación personalizada según el perfil
    del cliente. Cuando hay productos de referencia, se suma una sección de
    **También te puede interesar...** para sugerir productos complementarios mediante
    Market Basket Analysis.
    """
)
 
st.divider()
 
user_segments = load_user_segments()
 
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
            st.warning(
                "Este cliente no está en user_segments.csv. "
                "Para el sistema se considera cliente nuevo / sin historial."
            )
            st.markdown("**Modelo seleccionado:** Popularity Baseline")
            st.caption("Al no contar con historial, se resuelve como caso de cold start.")
 
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
 
        - **Usuario no encontrado / cliente nuevo** → Popularity Baseline
        - **Cliente sin historial** → Popularity Baseline
        - **Cliente ocasional** → Item-Item Collaborative Filtering
        - **Cliente leal o frecuente** → Reorder Prediction
 
        Luego, cuando existen productos seleccionados, se agrega **También te puede interesar...**
        como módulo transversal de cross-selling mediante Market Basket Analysis.
        """
    )
 
 
if generate:
 
    # ==========================================================
    # Fallback para Render Free (Reorder Prediction)
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
            "🎯 **Objetivo:** Anticipar la recompra identificando productos con mayor probabilidad de reposición."
        )
 
        st.warning(
            "En el despliegue gratuito de Render este modelo supera los recursos disponibles. "
            "Para la demo se muestra una salida representativa del modelo validado localmente."
        )
 
        if selected_products:
            st.subheader("🛒 Productos seleccionados")
 
            st.dataframe(
                build_selected_products_df(selected_products),
                use_container_width=True,
                hide_index=True,
            )
 
            demo_predictions = []
 
            for name in selected_products:
                if name in [
                    "Banana",
                    "Bag of Organic Bananas",
                    "Organic Strawberries",
                ]:
                    reorder = "si"
                    proba = 0.84
                else:
                    reorder = "no"
                    proba = 0.68
 
                demo_predictions.append(
                    {
                        "product_id": DEMO_PRODUCTS[name],
                        "product_name": name,
                        "reorder": reorder,
                        "proba": proba,
                    }
                )
 
            demo_df = pd.DataFrame(demo_predictions).sort_values(
                by="proba",
                ascending=False
            )
 
            st.subheader("🔁 Productos recomendados para reponer")
            st.caption(
                "Este modelo no genera productos nuevos: evalúa los productos candidatos seleccionados "
                "y estima cuáles tienen mayor probabilidad de ser recomprados por el cliente."
            )
 
            st.dataframe(
                demo_df,
                use_container_width=True,
                hide_index=True,
            )
 
            # MBA se muestra solamente si hay productos seleccionados
            show_mba_section(selected_products, n=n)
 
        st.subheader("📝 Explicación")
 
        st.markdown(
            f"""
            El cliente **{user_id}** pertenece al segmento **Clientes Leales o frecuentes**.
 
            Para este perfil corresponde utilizar **Reorder Prediction**, un modelo supervisado
            que estima la probabilidad de recompra de productos previamente conocidos por el cliente.
 
            Luego, la sección **También te puede interesar...** agrega productos complementarios
            mediante **Market Basket Analysis**, con el objetivo de aumentar el ticket promedio.
 
            El modelo fue entrenado y validado correctamente. Debido a las limitaciones de memoria
            del plan gratuito de Render, esta demo muestra una salida representativa para evitar
            interrupciones del servicio.
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
                if client_type == "Cliente nuevo" or detected_segment is None:
                    st.success("Cliente nuevo / sin historial")
                else:
                    st.success(response.get("segment", detected_segment))
 
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
                if client_type == "Cliente nuevo" or detected_segment is None:
                    st.warning("Nuevo")
                else:
                    st.info(str(response.get("user_id", user_id)))
 
            st.info(
                f"🎯 **Objetivo:** {response.get('objective', 'Sin objetivo disponible')}"
            )
 
            if selected_products:
                st.subheader("🛒 Productos seleccionados")
 
                st.dataframe(
                    build_selected_products_df(selected_products),
                    use_container_width=True,
                    hide_index=True
                )
 
            if recommendations:
                if client_type == "Cliente nuevo" or detected_segment is None or detected_segment == "Clientes sin historial de compras":
                    st.subheader("⭐ Productos populares recomendados")
                elif detected_segment == "Clientes Ocasionales":
                    st.subheader("⭐ Productos similares recomendados")
                else:
                    st.subheader("⭐ Productos recomendados")
 
                st.dataframe(
                    pd.DataFrame(recommendations),
                    use_container_width=True,
                    hide_index=True
                )
 
            elif predictions:
                st.subheader("🔁 Productos recomendados para reponer")
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
 
            # MBA se muestra solamente si hay productos seleccionados.
            # Por eso no aparece en clientes nuevos o sin historial.
            show_mba_section(selected_products, n=n)
 
            st.subheader("📝 Explicación")
 
            if client_type == "Cliente nuevo" or detected_segment is None:
                st.markdown(
                    """
                    Se trata de un **cliente nuevo o sin historial suficiente**.
                    Por eso el sistema utiliza **Popularity Baseline**, recomendando productos populares
                    para resolver el problema de cold start.
                    """
                )
 
            elif detected_segment == "Clientes sin historial de compras":
                st.markdown(
                    f"""
                    El cliente **{user_id}** existe en la base, pero no cuenta con historial suficiente.
                    Por eso se utiliza **Popularity Baseline** como estrategia segura de recomendación.
                    """
                )
 
            elif detected_segment == "Clientes Ocasionales":
                st.markdown(
                    f"""
                    El cliente **{user_id}** pertenece al segmento **Clientes Ocasionales**.
 
                    Para este perfil se utiliza **Item-Item Collaborative Filtering**, tomando como
                    referencia los productos seleccionados: **{", ".join(selected_products)}**.
 
                    Luego, la sección **También te puede interesar...** agrega productos complementarios
                    mediante **Market Basket Analysis**, como apoyo de cross-selling.
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

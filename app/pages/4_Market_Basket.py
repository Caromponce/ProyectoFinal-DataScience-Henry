# importar librerías
import pandas as pd
import streamlit as st

from src.styles import inject_css
from src.ui import henry_title, henry_tag
from src.mba_prod_recommender import MBA_Prod_Recommender
from src.mba_aisle_recommender import MBA_Aisle_Recommender


st.set_page_config(
    page_title="Market Basket",
    page_icon="🛒",
    layout="wide"
)

inject_css()


@st.cache_resource
def load_mba_product_model():
    return MBA_Prod_Recommender.load()


@st.cache_resource
def load_mba_aisle_model():
    return MBA_Aisle_Recommender.load()


def get_products_from_rules(model):
    product_ids = set()

    for antecedents in model.rules["antecedents"]:
        product_ids.update(list(antecedents))

    products = [
        {
            "product_id": int(product_id),
            "product_name": model.id_to_name.get(product_id, f"Producto {product_id}")
        }
        for product_id in product_ids
    ]

    return pd.DataFrame(products).sort_values("product_name")


def recommend_products_with_metrics(model, cart_product_ids, top_n=10):
    cart = set(cart_product_ids)

    applicable = model.rules[
        model.rules["antecedents"].apply(lambda antecedents: antecedents.issubset(cart))
    ]

    best_per_product = {}

    for _, rule in applicable.iterrows():
        for product_id in rule["consequents"]:
            if product_id in cart:
                continue

            if model.product_support.get(product_id, 0.0) > model.max_consequent_support:
                continue

            candidate = (
                rule["lift"],
                rule["confidence"],
                rule["support"],
                product_id
            )

            if product_id not in best_per_product or candidate[:2] > best_per_product[product_id][:2]:
                best_per_product[product_id] = candidate

    ranked = sorted(
        best_per_product.values(),
        key=lambda item: (item[0], item[1]),
        reverse=True
    )[:top_n]

    return pd.DataFrame(
        [
            {
                "rank": index + 1,
                "product_id": int(product_id),
                "product_name": model.id_to_name.get(product_id, f"Producto {product_id}"),
                "support": support,
                "confidence": confidence,
                "lift": lift
            }
            for index, (lift, confidence, support, product_id) in enumerate(ranked)
        ]
    )


def get_aisles_from_rules(model):
    aisle_ids = set()

    for antecedents in model.rules["antecedents"]:
        aisle_ids.update(list(antecedents))

    aisles = [
        {
            "aisle_id": int(aisle_id),
            "aisle_name": model.id_to_name.get(aisle_id, f"Pasillo {aisle_id}")
        }
        for aisle_id in aisle_ids
    ]

    return pd.DataFrame(aisles).sort_values("aisle_name")


def recommend_aisles_with_metrics(model, selected_aisle_id, top_n=10):
    applicable = model.rules[
        model.rules["antecedents"].apply(lambda antecedents: selected_aisle_id in antecedents)
    ]

    best_per_aisle = {}

    for _, rule in applicable.iterrows():
        for aisle_id in rule["consequents"]:
            if aisle_id == selected_aisle_id:
                continue

            if model.aisle_support.get(aisle_id, 0.0) > model.max_consequent_support:
                continue

            candidate = (
                rule["lift"],
                rule["confidence"],
                rule["support"],
                aisle_id
            )

            if aisle_id not in best_per_aisle or candidate[:2] > best_per_aisle[aisle_id][:2]:
                best_per_aisle[aisle_id] = candidate

    ranked = sorted(
        best_per_aisle.values(),
        key=lambda item: (item[0], item[1]),
        reverse=True
    )[:top_n]

    return pd.DataFrame(
        [
            {
                "rank": index + 1,
                "aisle_id": int(aisle_id),
                "aisle_name": model.id_to_name.get(aisle_id, f"Pasillo {aisle_id}"),
                "support": support,
                "confidence": confidence,
                "lift": lift
            }
            for index, (lift, confidence, support, aisle_id) in enumerate(ranked)
        ]
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


henry_tag("Market Basket Analysis")
henry_title("Carrito y Asociación de Productos")

st.markdown(
    """
    Explorador interactivo de reglas de asociación.  
    Permite analizar qué productos o pasillos suelen comprarse juntos para generar
    oportunidades de **cross-selling**.
    """
)

st.divider()

try:
    product_model = load_mba_product_model()
    aisle_model = load_mba_aisle_model()

    c1, c2, c3 = st.columns(3)
    c1.metric("Reglas por producto", f"{len(product_model.rules):,}".replace(",", "."))
    c2.metric("Reglas por pasillo", f"{len(aisle_model.rules):,}".replace(",", "."))
    c3.metric("Algoritmo", "FP-Growth")

    st.divider()

    analysis_type = st.radio(
        "Seleccioná el análisis",
        options=["Productos asociados", "Pasillos asociados"],
        horizontal=True
    )

    top_n = st.slider(
        "Cantidad de recomendaciones",
        min_value=1,
        max_value=10,
        value=5
    )

    if analysis_type == "Productos asociados":
        henry_tag("Explorador por producto")
        st.subheader("🛒 Seleccioná productos del carrito")

        products_df = get_products_from_rules(product_model)

        product_name_to_id = dict(
            zip(products_df["product_name"], products_df["product_id"])
        )

        selected_names = st.multiselect(
            "Productos con reglas disponibles",
            options=products_df["product_name"].tolist(),
            default=products_df["product_name"].head(1).tolist(),
            help="Se muestran solo productos que forman parte de reglas de asociación."
        )

        selected_ids = [
            int(product_name_to_id[name])
            for name in selected_names
        ]

        if selected_ids:
            result_df = recommend_products_with_metrics(
                product_model,
                selected_ids,
                top_n=top_n
            )

            st.success("Productos seleccionados como carrito de entrada:")
            st.dataframe(
                pd.DataFrame(
                    {
                        "product_id": selected_ids,
                        "product_name": selected_names
                    }
                ),
                use_container_width=True,
                hide_index=True
            )

            if not result_df.empty:
                st.subheader("⭐ Productos recomendados")

                display_df = result_df.rename(
                    columns={
                        "rank": "Ranking",
                        "product_id": "ID Producto",
                        "product_name": "Producto recomendado",
                        "support": "Frecuencia",
                        "confidence": "Probabilidad de recomendación",
                        "lift": "Fuerza de asociación"
                    }
                )

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )

                best = result_df.iloc[0]

                st.info(
                    f"""
                    Mejor recomendación: **{best["product_name"]}**  
                    Probabilidad de recomendación: **{best["confidence"]:.1%}**  
                    Fuerza de asociación: **{best["lift"]:.2f}**
                    """
                )
            else:
                st.warning("No se encontraron recomendaciones para ese carrito.")

    else:
        henry_tag("Explorador por pasillo")
        st.subheader("🏬 Seleccioná un pasillo")

        aisles_df = get_aisles_from_rules(aisle_model)

        aisle_name_to_id = dict(
            zip(aisles_df["aisle_name"], aisles_df["aisle_id"])
        )

        selected_aisle_name = st.selectbox(
            "Pasillos con reglas disponibles",
            options=aisles_df["aisle_name"].tolist(),
            help="Se muestran solo pasillos que forman parte de reglas de asociación."
        )

        selected_aisle_id = int(aisle_name_to_id[selected_aisle_name])

        result_df = recommend_aisles_with_metrics(
            aisle_model,
            selected_aisle_id,
            top_n=top_n
        )

        st.success(f"Pasillo seleccionado: **{selected_aisle_name}**")

        if not result_df.empty:
            st.subheader("⭐ Pasillos recomendados")

            display_df = result_df.rename(
                columns={
                    "rank": "Ranking",
                    "aisle_id": "ID Pasillo",
                    "aisle_name": "Pasillo recomendado",
                    "support": "Frecuencia",
                    "confidence": "Probabilidad de recomendación",
                    "lift": "Fuerza de asociación"
                }
            )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

            best = result_df.iloc[0]

            st.info(
                f"""
                Mejor recomendación: **{best["aisle_name"]}**  
                Probabilidad de recomendación: **{best["confidence"]:.1%}**  
                Fuerza de asociación: **{best["lift"]:.2f}**
                """
            )
        else:
            st.warning("No se encontraron recomendaciones para ese pasillo.")

    st.divider()

    henry_tag("Interpretación")

    st.markdown(
        """
### 🧠 ¿Cómo se interpreta?

- **Frecuencia** indica qué tan seguido aparece esa combinación en las compras.
- **Probabilidad de recomendación** indica qué tan probable es recomendar el producto o pasillo sugerido dado el carrito elegido.
- **Fuerza de asociación** mide qué tan fuerte es la relación frente a una compra aleatoria.

Una fuerza de asociación mayor a **1** indica que la relación es relevante.

Este análisis permite transformar patrones de compra en acciones comerciales:
recomendaciones inteligentes, combos, promociones cruzadas y sugerencias dentro del carrito.
"""
    )

except FileNotFoundError as error:
    st.error(
        "No se encontraron los modelos de Market Basket. "
        "En Render deberían descargarse automáticamente desde Google Drive."
    )
    st.code(str(error))

except Exception as error:
    st.error("Ocurrió un error al cargar Market Basket.")
    st.code(str(error))
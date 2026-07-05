# importar librerías
import streamlit as st
import pandas as pd

from src.styles import inject_css
from src.ui import henry_title, henry_tag


st.set_page_config(
    page_title="Market Basket",
    page_icon="🛒",
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

henry_tag("Market Basket Analysis")
henry_title("Carrito y Asociación de Productos")

st.markdown(
    """
    Esta sección muestra reglas reales de asociación entre productos y pasillos.
    El objetivo es identificar qué combinaciones suelen comprarse juntas para
    generar oportunidades de **cross-selling**.
    """
)

st.divider()

c1, c2, c3 = st.columns(3)
c1.metric("Reglas por producto", "1.803")
c2.metric("Reglas por pasillo", "11.021")
c3.metric("Algoritmo", "FP-Growth")

st.divider()

product_rules = [
    {
        "antecedents": "Non Fat Acai & Mixed Berries Yogurt",
        "consequents": "Icelandic Style Skyr Blueberry Non-fat Yogurt",
        "support": 0.0012,
        "confidence": 0.453,
        "lift": 75.65
    },
    {
        "antecedents": "Icelandic Style Skyr Blueberry Non-fat Yogurt",
        "consequents": "Non Fat Acai & Mixed Berries Yogurt",
        "support": 0.0012,
        "confidence": 0.204,
        "lift": 75.65
    },
    {
        "antecedents": "Grapefruit Sparkling Water",
        "consequents": "Lemon Sparkling Water",
        "support": 0.0010,
        "confidence": 0.223,
        "lift": 75.63
    }
]

aisle_rules = [
    {
        "antecedents": "fresh fruits + dry pasta",
        "consequents": "pasta sauce + fresh vegetables",
        "support": 0.0100,
        "confidence": 0.207,
        "lift": 5.12
    },
    {
        "antecedents": "pasta sauce + fresh vegetables",
        "consequents": "fresh fruits + dry pasta",
        "support": 0.0100,
        "confidence": 0.248,
        "lift": 5.12
    },
    {
        "antecedents": "fresh vegetables + dry pasta",
        "consequents": "fresh fruits + pasta sauce",
        "support": 0.0100,
        "confidence": 0.212,
        "lift": 5.01
    }
]

product_df = pd.DataFrame(product_rules)
aisle_df = pd.DataFrame(aisle_rules)

st.subheader("🏆 Regla más fuerte por producto")

best_rule = product_df.sort_values(by="lift", ascending=False).iloc[0]

st.success(
    f"""
    Si un usuario compra:

    **{best_rule["antecedents"]}**

    entonces podría recomendarse:

    **{best_rule["consequents"]}**

    Lift = **{best_rule["lift"]:.2f}**
    """
)

st.divider()

henry_tag("Reglas por producto")

st.subheader("🛒 Productos que suelen comprarse juntos")

for _, row in product_df.iterrows():
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.info(f"🧺 {row['antecedents']}")

    with col2:
        st.markdown(
            """
            <div style='text-align:center; font-size:32px; font-weight:bold;'>
                ➜
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.warning(f"⭐ Recomendar: {row['consequents']}")

    st.caption(
        f"Support: {row['support']:.4f} | "
        f"Confidence: {row['confidence']:.3f} | "
        f"Lift: {row['lift']:.2f}"
    )

    st.divider()

henry_tag("Reglas por pasillo")

st.subheader("🏬 Pasillos que suelen comprarse juntos")

for _, row in aisle_df.iterrows():
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.info(f"🧺 {row['antecedents']}")

    with col2:
        st.markdown(
            """
            <div style='text-align:center; font-size:32px; font-weight:bold;'>
                ➜
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.warning(f"⭐ Recomendar: {row['consequents']}")

    st.caption(
        f"Support: {row['support']:.4f} | "
        f"Confidence: {row['confidence']:.3f} | "
        f"Lift: {row['lift']:.2f}"
    )

    st.divider()

henry_tag("Detalle")

st.subheader("📋 Tabla de reglas por producto")

product_table = product_df.rename(
    columns={
        "antecedents": "Productos comprados",
        "consequents": "Producto recomendado",
        "support": "Support",
        "confidence": "Confidence",
        "lift": "Lift"
    }
)

st.dataframe(
    product_table,
    use_container_width=True,
    hide_index=True
)

st.subheader("📋 Tabla de reglas por pasillo")

aisle_table = aisle_df.rename(
    columns={
        "antecedents": "Pasillos comprados",
        "consequents": "Pasillos recomendados",
        "support": "Support",
        "confidence": "Confidence",
        "lift": "Lift"
    }
)

st.dataframe(
    aisle_table,
    use_container_width=True,
    hide_index=True
)

st.divider()

henry_tag("Interpretación")

st.markdown(
    """
### 🧠 ¿Cómo se interpreta?

- **Support** indica qué tan frecuente aparece la combinación en el dataset.
- **Confidence** indica la probabilidad de que se compre el producto recomendado dado el antecedente.
- **Lift** mide qué tan fuerte es la asociación frente a una compra aleatoria.

Un **lift mayor a 1** indica que la asociación entre productos o pasillos es relevante.

En este proyecto se aplicó además un filtro para evitar recomendaciones demasiado obvias,
como productos globalmente muy populares que el usuario probablemente compraría de todos modos.
"""
)
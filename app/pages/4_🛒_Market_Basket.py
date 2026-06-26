# importar librerías
import streamlit as st
import pandas as pd

# importar cliente
from src.api_client import get_market_basket

# importar estilos Henry
from src.styles import inject_css
from src.ui import henry_title, henry_tag


st.set_page_config(
    page_title="Carrito",
    page_icon="🛒",
    layout="wide"
)

inject_css()

with st.sidebar:

    st.image(
        "assets/logo_data_horizon.png",
        width=150
    )

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
    
henry_tag("Market Basket Analysis")
henry_title("Carrito y Asociación de Productos")

st.markdown(
    """
    Esta sección muestra reglas de asociación entre productos.
    El objetivo es identificar qué productos suelen comprarse juntos
    para generar oportunidades de **cross-selling**.
    """
)

st.divider()

market_basket = get_market_basket()
rules_df = pd.DataFrame(market_basket["rules"])

best_rule = rules_df.sort_values(
    by="lift",
    ascending=False
).iloc[0]

st.subheader("🏆 Regla más fuerte")

st.success(
    f"""
    Si un usuario compra:

    **{best_rule["antecedents"]}**

    entonces podría recomendarse:

    **{best_rule["consequents"]}**

    Lift = **{best_rule["lift"]}**
    """
)

st.divider()

henry_tag("Reglas de asociación")
st.subheader("🛒 Productos que suelen comprarse juntos")

for index, row in rules_df.iterrows():

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
        f"Support: {row['support']} | Confidence: {row['confidence']} | Lift: {row['lift']}"
    )

    st.divider()

henry_tag("Detalle")
st.subheader("📋 Tabla de reglas")

rules_table = rules_df.rename(
    columns={
        "antecedents": "Productos comprados",
        "consequents": "Producto recomendado",
        "support": "Support",
        "confidence": "Confidence",
        "lift": "Lift"
    }
)

st.dataframe(
    rules_table,
    use_container_width=True,
    hide_index=True
)

henry_tag("Interpretación")

st.markdown(
    """
### 🧠 ¿Cómo se interpreta?

- **Support** indica qué tan frecuente aparece la combinación en el dataset.
- **Confidence** indica la probabilidad de que se compre el producto recomendado dado el antecedente.
- **Lift** mide qué tan fuerte es la asociación frente a una compra aleatoria.

Un lift mayor a 1 indica que la asociación entre productos es relevante.
"""
)
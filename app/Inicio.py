# importar librerías
import streamlit as st

from src.styles import inject_css
from src.ui import henry_title, henry_tag, henry_bullet


st.set_page_config(
    page_title="Data Horizon | Inicio",
    page_icon="📊",
    layout="wide"
)

inject_css()

with st.sidebar:
    st.image("assets/logo_data_horizon.png", width=150)


henry_tag("Proyecto Final | Henry Data Science")
henry_title("Sistema Inteligente de Recomendación de Productos")

st.markdown(
    """
    **Desarrollado por Data Horizon.**  
    Una solución analítica basada en segmentación de usuarios, modelos de
    recomendación y reglas de asociación para generar recomendaciones
    personalizadas y oportunidades de cross-selling.
    """
)

st.divider()


# ==========================
# Estado del sistema
# ==========================

henry_tag("Estado del sistema")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.markdown(
        """
        <div class="status-card">
            <div class="status-title">🟢 Dashboard</div>
            <div class="status-value status-ok">Operativo</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with status_col2:
    st.markdown(
        """
        <div class="status-card">
            <div class="status-title">🟢 FastAPI</div>
            <div class="status-value status-ok">Funcionando</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with status_col3:
    st.markdown(
        """
        <div class="status-card">
            <div class="status-title">🟢 Modelos ML</div>
            <div class="status-value status-ok">Integrados</div>
        </div>
        """,
        unsafe_allow_html=True
    )

status_col4, status_col5 = st.columns(2)

with status_col4:
    st.markdown(
        """
        <div class="status-card">
            <div class="status-title">🟢 Recomendador</div>
            <div class="status-value status-ok">Conectado</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with status_col5:
    st.markdown(
        """
        <div class="status-card">
            <div class="status-title">🟢 Deploy Cloud</div>
            <div class="status-value status-ok">Render activo</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()


# ==========================
# Data Horizon + arquitectura
# ==========================

left_col, right_col = st.columns([1, 2])

with left_col:
    henry_tag("Data Horizon")

    st.subheader("🎯 Misión")

    st.markdown(
        """
        Transformar datos en decisiones mediante soluciones analíticas
        y sistemas de recomendación que mejoren la experiencia de los
        usuarios y generen valor para los negocios.
        """
    )

    st.subheader("👥 Equipo")

    st.markdown(
        """
        **Carolina Ponce**  
        Data Scientist

        **Felix Augusto Fernandez Gonzalez**  
        Data Scientist

        **Yael Authier**  
        Data Scientist
        """
    )

with right_col:
    henry_tag("Arquitectura")

    st.subheader("⚙️ Arquitectura del sistema")

    st.image(
        "assets/architecture.png",
        use_container_width=True
    )

st.divider()


# ==========================
# Sistema híbrido
# ==========================

henry_tag("Sistema híbrido")

st.subheader("🧠 ¿Cómo decide el recomendador?")

st.markdown(
    """
    El sistema funciona como un **router inteligente**: primero identifica el
    tipo de cliente y luego selecciona la estrategia de recomendación más adecuada.
    """
)

flow_col1, flow_col2, flow_col3 = st.columns(3)

with flow_col1:
    st.markdown(
        """
        <div class="henry-card">
            <h3>👤 Sin historial</h3>
            <p><strong>Modelo:</strong> Popularity Baseline</p>
            <p>Recomienda productos populares para resolver el problema de cold start.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with flow_col2:
    st.markdown(
        """
        <div class="henry-card">
            <h3>🔵 Cliente ocasional</h3>
            <p><strong>Modelo:</strong> Item-Item Collaborative Filtering</p>
            <p>Recomienda productos similares según patrones de compra de otros usuarios.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with flow_col3:
    st.markdown(
        """
        <div class="henry-card">
            <h3>🔴 Cliente leal</h3>
            <p><strong>Modelo:</strong> Reorder Prediction</p>
            <p>Anticipa qué productos tienen mayor probabilidad de recompra.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.info(
    """
    Luego de la recomendación personalizada, el sistema puede sumar la sección
    **“También te puede interesar...”**, basada en **Market Basket Analysis**, para
    sugerir productos complementarios y aumentar el valor del carrito.
    """
)

st.divider()


# ==========================
# Stack tecnológico
# ==========================

henry_tag("Stack tecnológico")

tech1, tech2, tech3, tech4 = st.columns(4)

with tech1:
    st.info("🐍 **Python**")

with tech2:
    st.info("📊 **Pandas**")

with tech3:
    st.info("🤖 **Scikit-learn**")

with tech4:
    st.info("🌐 **Streamlit**")

tech5, tech6, tech7, tech8 = st.columns(4)

with tech5:
    st.info("⚡ **FastAPI**")

with tech6:
    st.info("🧠 **XGBoost**")

with tech7:
    st.info("🛒 **Market Basket**")

with tech8:
    st.info("☁️ **Render**")

tech9, tech10, tech11, tech12 = st.columns(4)

with tech9:
    st.info("🐙 **GitHub**")

with tech10:
    st.info("📈 **Plotly**")

with tech11:
    st.info("🔗 **Joblib**")

with tech12:
    st.info("📦 **Google Drive**")

st.divider()


# ==========================
# Flujo del sistema
# ==========================

henry_tag("Flujo del sistema")

henry_bullet("El usuario ingresa a la interfaz desarrollada en Streamlit.")
henry_bullet("La aplicación consulta la API o utiliza datos precalculados cuando el entorno cloud requiere optimización.")
henry_bullet("FastAPI segmenta al usuario y selecciona la estrategia correspondiente.")
henry_bullet("El sistema genera una recomendación personalizada: Popularity, Item-Item CF o Reorder Prediction.")
henry_bullet("Cuando hay productos de referencia, Market Basket Analysis agrega sugerencias complementarias en la sección “También te puede interesar...”.")
henry_bullet("La app devuelve resultados interpretables, métricas explicativas y tablas listas para analizar.")

st.divider()

st.caption(
    "Data Horizon · Proyecto Final Henry Data Science · Sistema Inteligente de Recomendación de Productos"
)


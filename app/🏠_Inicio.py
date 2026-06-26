# importar librerías
import streamlit as st

# importar estilos Henry
from src.styles import inject_css
from src.ui import henry_title, henry_tag, henry_bullet


st.set_page_config(
    page_title="Data Horizon | Inicio",
    page_icon="📊",
    layout="wide"
)

inject_css()

with st.sidebar:

    st.image(
        "assets/logo_data_horizon.png",
        width=150
    )


# -----------------------------
# Header
# -----------------------------

henry_tag("Proyecto Final | Henry Data Science")
henry_title("Sistema Inteligente de Recomendación de Productos")

st.markdown(
    """
    **Desarrollado por Data Horizon.**  
    Una solución analítica para generar recomendaciones personalizadas
    a partir del comportamiento de compra de los usuarios.
    """
)

st.divider()


# -----------------------------
# Estado del sistema
# -----------------------------

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
            <div class="status-title">🟢 Mock API</div>
            <div class="status-value status-ok">Activa</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with status_col3:
    st.markdown(
        """
        <div class="status-card">
            <div class="status-title">🟡 FastAPI</div>
            <div class="status-value status-progress">En integración</div>
        </div>
        """,
        unsafe_allow_html=True
    )

status_col4, status_col5 = st.columns(2)

with status_col4:
    st.markdown(
        """
        <div class="status-card">
            <div class="status-title">🟡 Modelos ML</div>
            <div class="status-value status-progress">En integración</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with status_col5:
    st.markdown(
        """
        <div class="status-card">
            <div class="status-title">⚪ Deploy</div>
            <div class="status-value status-pending">Pendiente</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()


# -----------------------------
# Misión + Arquitectura
# -----------------------------

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


# -----------------------------
# Tecnologías
# -----------------------------

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
    st.info("🐙 **GitHub**")

with tech7:
    st.info("🔁 **GitHub Actions**")

with tech8:
    st.info("🧠 **Recommender Systems**")

st.divider()


# -----------------------------
# Flujo
# -----------------------------

henry_tag("Flujo del sistema")

henry_bullet("El usuario ingresa a la interfaz desarrollada en Streamlit.")
henry_bullet("Streamlit envía el user_id a la API.")
henry_bullet("FastAPI identifica el segmento del usuario.")
henry_bullet("El sistema selecciona el motor de recomendación adecuado.")
henry_bullet("Se devuelven recomendaciones personalizadas con explicación y KPIs.")

st.divider()

st.caption(
    "Data Horizon · Proyecto Final Henry Data Science · Sistema Inteligente de Recomendación de Productos"
)
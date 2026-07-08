# importar librerías
import json
from pathlib import Path
 
import pandas as pd
import streamlit as st
 
from src.styles import inject_css
from src.ui import henry_title, henry_tag
 
 
st.set_page_config(
    page_title="KPIs",
    page_icon="📊",
    layout="wide"
)
 
inject_css()
 
BASE_DIR = Path(__file__).resolve().parents[2]
METRICS_PATH = BASE_DIR / "data" / "processed" / "dashboard_metrics.json"
 
 
@st.cache_data
def load_metrics():
    """
    Carga las métricas calculadas durante el entrenamiento/evaluación.
    Si el archivo no existe o falta alguna clave, se devuelven valores seguros
    para evitar que la página se rompa en Render.
    """
 
    default_data = {
        "total_users": 0,
        "total_products": 0,
        "total_interactions": 0,
        "sparsity": 0,
        "kmeans": {
            "k": 0,
            "silhouette": 0,
            "davies_bouldin": 0,
        },
        "models": [],
    }
 
    if not METRICS_PATH.exists():
        return default_data
 
    with open(METRICS_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
 
    for key, value in default_data.items():
        data.setdefault(key, value)
 
    return data
 
 
def format_number(value):
    """Formatea números grandes con punto como separador de miles."""
 
    try:
        return f"{int(value):,}".replace(",", ".")
    except Exception:
        return "-"
 
 
def format_metric_value(value):
    """Formatea métricas para mostrarlas en tablas."""
 
    if value is None or pd.isna(value):
        return "-"
 
    try:
        value = float(value)
    except Exception:
        return str(value)
 
    if value < 1:
        return f"{value:.4f}"
 
    return f"{int(value):,}".replace(",", ".")
 
 
def normalize_model_name(model_name):
    """
    Normaliza nombres porque el JSON puede tener nombres cortos
    y la interfaz necesita nombres más claros para la demo.
    """
 
    model_name = str(model_name)
 
    name_map = {
        "Popularity": "Popularity Baseline",
        "Popularity Model": "Popularity Baseline",
        "Popularity Baseline": "Popularity Baseline",
        "Item-Item Collaborative Filtering": "Item-Item Collaborative Filtering",
        "Market Basket Analysis": "Market Basket Analysis (Products)",
        "Market Basket Analysis (Products)": "Market Basket Analysis (Products)",
        "Market Basket Analysis (Aisles)": "Market Basket Analysis (Aisles)",
        "Reorder Prediction": "Reorder Prediction (XGBoost)",
        "Reorder Prediction (XGBoost)": "Reorder Prediction (XGBoost)",
    }
 
    return name_map.get(model_name, model_name)
 
 
def build_performance_table(models):
    """Construye una tabla de performance robusta para la página."""
 
    if not models:
        return pd.DataFrame(
            columns=[
                "Modelo",
                "Caso de uso",
                "Métrica principal",
                "Valor",
                "Notas",
                "Valor numérico",
            ]
        )
 
    models_df = pd.DataFrame(models)
 
    # Asegurar columnas esperadas aunque falten en el JSON.
    for column in ["model", "use_case", "main_metric", "value", "notes"]:
        if column not in models_df.columns:
            models_df[column] = None
 
    models_df["Modelo"] = models_df["model"].apply(normalize_model_name)
    models_df["Caso de uso"] = models_df["use_case"].fillna("-")
    models_df["Métrica principal"] = models_df["main_metric"].fillna("-")
    models_df["Valor"] = models_df["value"].apply(format_metric_value)
    models_df["Valor numérico"] = models_df["value"]
    models_df["Notas"] = models_df["notes"].fillna("-")
 
    return models_df[
        [
            "Modelo",
            "Caso de uso",
            "Métrica principal",
            "Valor",
            "Notas",
            "Valor numérico",
        ]
    ]
 
 
MODEL_INFO = {
    "Popularity Baseline": {
        "caso_uso": "Clientes nuevos o sin historial",
        "metrica": "No aplica",
        "descripcion": (
            "Modelo no personalizado utilizado para resolver el problema de cold start. "
            "Recomienda los productos con mayor popularidad histórica cuando el cliente "
            "todavía no posee historial suficiente."
        ),
        "porque": (
            "Fue incorporado para garantizar que el sistema pueda recomendar desde la "
            "primera interacción, incluso cuando no existe información previa del usuario."
        ),
        "interpretacion": (
            "No se interpreta como un modelo predictivo personalizado. Funciona como una "
            "línea base estable para usuarios nuevos o sin historial de compra."
        ),
    },
    "Item-Item Collaborative Filtering": {
        "caso_uso": "Clientes ocasionales",
        "metrica": "Recall@10",
        "descripcion": (
            "Calcula similitud entre productos utilizando el historial de compras de los clientes. "
            "Cuando se toma un producto como referencia, recomienda otros productos con patrones "
            "de consumo similares."
        ),
        "porque": (
            "Fue seleccionado para clientes ocasionales porque permite recomendar productos "
            "relacionados aunque el historial individual del usuario sea limitado."
        ),
        "interpretacion": (
            "Recall@10 indica qué proporción de productos realmente comprados aparece dentro "
            "de las primeras diez recomendaciones del modelo."
        ),
    },
    "Market Basket Analysis (Products)": {
        "caso_uso": "Cross-selling / También te puede interesar",
        "metrica": "Reglas de asociación",
        "descripcion": (
            "Identifica productos que suelen comprarse juntos dentro de un mismo carrito. "
            "En la app se utiliza como módulo complementario bajo la sección "
            "'También te puede interesar...'."
        ),
        "porque": (
            "Fue seleccionado porque permite generar recomendaciones complementarias y "
            "acciones comerciales orientadas a aumentar el ticket promedio."
        ),
        "interpretacion": (
            "No se evalúa con Recall como los recomendadores personalizados. Se interpreta "
            "mediante reglas de asociación, considerando soporte, confianza y lift."
        ),
    },
    "Market Basket Analysis (Aisles)": {
        "caso_uso": "Recomendación por pasillos / categorías",
        "metrica": "Reglas de asociación",
        "descripcion": (
            "Extiende Market Basket Analysis al nivel de pasillos para detectar categorías "
            "que suelen comprarse conjuntamente."
        ),
        "porque": (
            "Permite recomendar categorías completas y diseñar promociones cruzadas por familia "
            "de productos, no solamente por producto individual."
        ),
        "interpretacion": (
            "Se interpreta mediante reglas de asociación entre categorías. Es útil para entender "
            "relaciones de compra a nivel más agregado."
        ),
    },
    "Reorder Prediction (XGBoost)": {
        "caso_uso": "Clientes leales o frecuentes",
        "metrica": "PR-AUC",
        "descripcion": (
            "Modelo supervisado entrenado para estimar la probabilidad de recompra de cada "
            "producto por cliente. No busca productos nuevos desde cero: ordena productos "
            "candidatos según probabilidad de recompra."
        ),
        "porque": (
            "Fue seleccionado para clientes leales porque permite anticipar necesidades de "
            "reposición y mejorar la experiencia del usuario frecuente."
        ),
        "interpretacion": (
            "PR-AUC es adecuada para problemas de clasificación con clases desbalanceadas. "
            "Un valor más alto indica mejor capacidad para separar productos que serán recomprados "
            "de aquellos que no."
        ),
    },
}
 
 
with st.sidebar:
    st.image("assets/logo_data_horizon.png", width=120)
 
 
henry_tag("Evaluación de modelos")
henry_title("KPIs del Sistema")
 
st.write(
    """
    El sistema implementa una arquitectura híbrida de recomendación.
    Primero identifica el tipo de cliente, luego selecciona la estrategia principal
    y finalmente puede complementar la recomendación con productos asociados mediante
    Market Basket Analysis.
    """
)
 
st.divider()
 
data = load_metrics()
 
 
# ==========================
# KPIs generales
# ==========================
 
c1, c2, c3, c4 = st.columns(4)
 
c1.metric("Usuarios", format_number(data.get("total_users", 0)))
c2.metric("Productos", format_number(data.get("total_products", 0)))
c3.metric("Interacciones", format_number(data.get("total_interactions", 0)))
c4.metric("Sparsity", f"{float(data.get('sparsity', 0)):.2f}%")
 
st.divider()
 
 
# ==========================
# Arquitectura del recomendador
# ==========================
 
henry_tag("Arquitectura híbrida")
st.subheader("🧠 Estrategias de recomendación")
 
router_df = pd.DataFrame(
    [
        {
            "Segmento / Caso de uso": "Cliente nuevo / sin historial",
            "Modelo seleccionado": "Popularity Baseline",
            "Objetivo": "Resolver el problema de cold start recomendando productos populares.",
        },
        {
            "Segmento / Caso de uso": "Cliente existente sin historial suficiente",
            "Modelo seleccionado": "Popularity Baseline",
            "Objetivo": "Mantener recomendaciones estables cuando el historial individual es insuficiente.",
        },
        {
            "Segmento / Caso de uso": "Cliente ocasional",
            "Modelo seleccionado": "Item-Item Collaborative Filtering",
            "Objetivo": "Recomendar productos similares según patrones de compra de otros usuarios.",
        },
        {
            "Segmento / Caso de uso": "Cliente leal o frecuente",
            "Modelo seleccionado": "Reorder Prediction",
            "Objetivo": "Anticipar la recompra y sugerir productos para reponer.",
        },
        {
            "Segmento / Caso de uso": "Complemento transversal",
            "Modelo seleccionado": "Market Basket Analysis",
            "Objetivo": "Mostrar 'También te puede interesar...' para aumentar el ticket mediante cross-selling.",
        },
    ]
)
 
st.dataframe(
    router_df,
    use_container_width=True,
    hide_index=True,
)
 
st.info(
    """
    El valor del sistema no está en elegir un único modelo ganador, sino en combinar
    la recomendación personalizada con una capa comercial de productos complementarios.
    """
)
 
st.divider()
 
 
# ==========================
# Segmentación
# ==========================
 
henry_tag("Segmentación")
st.subheader("👥 Métricas del modelo K-Means")
 
kmeans = data.get("kmeans", {})
 
k1, k2, k3 = st.columns(3)
 
k1.metric("Clusters", kmeans.get("k", "-"))
k2.metric("Silhouette Score", f"{float(kmeans.get('silhouette', 0)):.4f}")
k3.metric("Davies-Bouldin", f"{float(kmeans.get('davies_bouldin', 0)):.4f}")
 
st.caption(
    "La segmentación permite asignar cada usuario a una estrategia de recomendación acorde a su comportamiento."
)
 
st.divider()
 
 
# ==========================
# Performance de modelos
# ==========================
 
henry_tag("Performance")
st.subheader("📈 Desempeño de modelos")
 
performance_table = build_performance_table(data.get("models", []))
 
if performance_table.empty:
    st.warning("No se encontraron métricas de modelos en dashboard_metrics.json.")
else:
    st.dataframe(
        performance_table[
            [
                "Modelo",
                "Caso de uso",
                "Métrica principal",
                "Valor",
                "Notas",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )
 
st.divider()
 
 
# ==========================
# Explorador de modelos
# ==========================
 
st.subheader("🔎 Explorador interactivo de modelos")
 
if performance_table.empty:
    st.info("No hay modelos disponibles para explorar.")
else:
    model_options = performance_table["Modelo"].drop_duplicates().tolist()
 
    selected_model = st.selectbox(
        "Seleccioná un modelo",
        model_options,
    )
 
    selected = performance_table[
        performance_table["Modelo"] == selected_model
    ].iloc[0]
 
    info = MODEL_INFO.get(
        selected_model,
        {
            "caso_uso": selected.get("Caso de uso", "-"),
            "metrica": selected.get("Métrica principal", "-"),
            "descripcion": selected.get("Notas", "-"),
            "porque": "Este modelo forma parte de la arquitectura híbrida del sistema.",
            "interpretacion": "La interpretación depende de la métrica utilizada para este modelo.",
        },
    )
 
    caso_uso = selected.get("Caso de uso", info["caso_uso"])
    metrica = selected.get("Métrica principal", info["metrica"])
    valor = selected.get("Valor", "-")
 
    st.markdown(
        f"""
<div class="henry-card">
 
### {selected_model}
 
**Caso de uso**
 
{caso_uso}
 
---
 
**Métrica principal**
 
{metrica}
 
**Resultado obtenido**
 
{valor}
 
---
 
**¿Qué hace este modelo?**
 
{info["descripcion"]}
 
---
 
**¿Por qué fue seleccionado?**
 
{info["porque"]}
 
---
 
**¿Cómo interpretar este resultado?**
 
{info["interpretacion"]}
 
</div>
""",
        unsafe_allow_html=True,
    )
 
st.divider()
 
 
# ==========================
# Reorder Prediction
# ==========================
 
henry_tag("Modelo supervisado")
st.subheader("🏆 Reorder Prediction - XGBoost")
 
models_raw = pd.DataFrame(data.get("models", []))
 
if not models_raw.empty and "model" in models_raw.columns:
    models_raw["model_normalized"] = models_raw["model"].apply(normalize_model_name)
    reorder_rows = models_raw[
        models_raw["model_normalized"] == "Reorder Prediction (XGBoost)"
    ]
else:
    reorder_rows = pd.DataFrame()
 
if reorder_rows.empty:
    st.warning("No se encontraron métricas específicas de Reorder Prediction en el JSON.")
else:
    reorder = reorder_rows.iloc[0]
 
    r1, r2, r3, r4 = st.columns(4)
 
    r1.metric("PR-AUC", format_metric_value(reorder.get("value")))
    r2.metric("Precision", format_metric_value(reorder.get("precision")))
    r3.metric("Recall", format_metric_value(reorder.get("recall")))
    r4.metric("F1 Score", format_metric_value(reorder.get("f1")))
 
    st.success(
        f"""
        **Modelo supervisado seleccionado:** XGBoost.
 
        Fue elegido para clientes leales o frecuentes porque permite estimar la probabilidad
        de recompra de productos candidatos. En Render Free se utiliza una salida precalculada
        del modelo validado localmente para mantener estable el despliegue.
        """
    )
 
st.divider()
 
 
# ==========================
# Lectura final
# ==========================
 
henry_tag("Conclusiones")
 
st.markdown(
    """
### ✅ Lectura de resultados
 
- El sistema no utiliza un único algoritmo de recomendación.
- Primero identifica si el usuario tiene historial suficiente.
- Si el usuario es nuevo o no tiene historial, utiliza **Popularity Baseline**.
- Si el usuario es ocasional, utiliza **Item-Item Collaborative Filtering** para recomendar productos similares.
- Si el usuario es leal o frecuente, utiliza **Reorder Prediction** para anticipar recompra.
- La sección **También te puede interesar...** utiliza **Market Basket Analysis** como capa transversal de cross-selling.
- La arquitectura final combina personalización, recompra y productos complementarios dentro de un mismo flujo de recomendación.
"""
)

<p align="center">

# 🛒 Sistema Inteligente de Recomendación de Productos

### Proyecto Final · Henry Data Science

Arquitectura híbrida de Machine Learning para recomendaciones personalizadas sobre Instacart

</p>

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?logo=scikitlearn)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-success)
![Render](https://img.shields.io/badge/Deploy-Render-46E3B7)

> **Proyecto Final | Henry Data Science**  
> Desarrollado por **Data Horizon**, una solución de Machine Learning orientada a generar recomendaciones personalizadas mediante una arquitectura híbrida de modelos.

---

# 📌 Descripción

Este proyecto implementa un **Sistema Inteligente de Recomendación de Productos** utilizando el dataset público **Instacart Market Basket Analysis**.

A diferencia de un recomendador tradicional basado en un único algoritmo, la solución implementa una **arquitectura híbrida**, donde múltiples modelos de Machine Learning trabajan de manera coordinada.

El sistema analiza el comportamiento del usuario, determina automáticamente su segmento y selecciona la estrategia de recomendación más adecuada para cada caso.

Entre las técnicas implementadas se incluyen:

- Segmentación de usuarios mediante K-Means.
- Recomendación por Popularidad (Cold Start).
- Filtrado Colaborativo Item-Item.
- Market Basket Analysis mediante FP-Growth.
- Predicción de recompra utilizando XGBoost.

Todo el sistema se encuentra desplegado en la nube mediante **Render**, utilizando **Docker**, **FastAPI** y **Streamlit**.

---

## 🌐 Demo

🚀 **Aplicación**

https://proyectofinal-datascience-henry.onrender.com

📦 **Repositorio**

https://github.com/Caromponce/ProyectoFinal-DataScience-Henry


---

# 🏗️ Arquitectura del Sistema

El sistema implementa una **arquitectura híbrida de recomendación**, donde la API selecciona automáticamente la estrategia más adecuada según el comportamiento del usuario y el contexto de compra.

La solución integra múltiples modelos de Machine Learning especializados, orquestados mediante FastAPI y consumidos desde una interfaz desarrollada en Streamlit. Los modelos entrenados se descargan dinámicamente desde Google Drive al iniciar el contenedor Docker desplegado en Render.

<p align="center">
  <img src="assets/architecture.png" alt="Arquitectura del Sistema" width="1000">
</p>

# 📸 Capturas de la aplicación

## Recomendador de productos

<p align="center">
  <img src="assets/Recomendador.jpg" width="900">
</p>

## Segmentación de usuarios

<p align="center">
  <img src="assets/segmentacion.jpg" width="900">
</p>

## Market Basket Analysis

<p align="center">
  <img src="assets/Market.jpg" width="900">
</p>

## KPIs del sistema

<p align="center">
  <img src="assets/kpi.jpg" width="900">
</p>


---

# ⚙ Stack Tecnológico

## Lenguajes

- Python
- Pandas
- NumPy

## Machine Learning

- Scikit-Learn
- XGBoost
- LightGBM
- CatBoost
- mlxtend

## Backend

- FastAPI
- Uvicorn

## Frontend

- Streamlit

## DevOps

- Docker
- Render
- GitHub
- Google Drive

---

# 📂 Estructura del proyecto

```

ProyectoFinal-DataScience-Henry/

├── api/
├── app/
├── assets/
├── docs/
├── notebooks/
├── src/
├── Dockerfile
├── download_models.py
├── start.sh
├── requirements.txt
└── README.md

```

---

# 📊 Dataset

El proyecto utiliza el dataset público **Instacart Market Basket Analysis**, que contiene el historial anonimizado de compras de un supermercado online.

### Resumen

| Indicador | Valor |
|-----------|------:|
| Usuarios | 206.209 |
| Productos | 49.688 |
| Interacciones | 32.434.489 |
| Pasillos | 134 |
| Departamentos | 21 |
| Sparsity | 99.68% |
| Tasa de recompra | 58.97% |

### Archivos del dataset

| Tabla | Filas |
|--------|-------:|
| orders.csv | 3.421.083 |
| products.csv | 49.688 |
| aisles.csv | 134 |
| departments.csv | 21 |
| order_products__prior.csv | 32.434.489 |
| order_products__train.csv | 1.384.617 |

Durante el análisis exploratorio se identificó una matriz Usuario–Producto altamente dispersa (99.68% de sparsity), una tasa de recompra cercana al 59% y una distribución de productos con comportamiento **Long Tail**, características que motivaron la implementación de una arquitectura híbrida de recomendación.

---

# 🤖 Modelos Implementados

## Resumen de modelos

| Modelo | Tipo | Caso de uso | Estado |
|---------|------|-------------|:------:|
| Popularity Baseline | Baseline | Usuarios sin historial (Cold Start) | ✅ |
| K-Means | No supervisado | Segmentación de usuarios | ✅ |
| Item-Item Collaborative Filtering | Filtrado colaborativo | Clientes ocasionales | ✅ |
| Market Basket Analysis (Producto) | Reglas de asociación | Productos complementarios | ✅ |
| Market Basket Analysis (Pasillos) | Reglas de asociación | Categorías relacionadas | ✅ |
| Reorder Prediction (XGBoost) | Supervisado | Clientes frecuentes | ✅ |

## Popularity Baseline

**Objetivo**

Resolver el problema de Cold Start para usuarios sin historial.

**Entrada**

Usuario nuevo.

**Salida**

Productos más populares.

---

## Segmentación de Usuarios (K-Means)

El modelo agrupa automáticamente los usuarios según su comportamiento de compra.

Segmentos obtenidos:

- Clientes sin historial
- Clientes Ocasionales
- Clientes Leales
- Clientes de Canasta Grande

Este modelo **no genera recomendaciones**, sino que determina qué estrategia utilizar posteriormente.

---

## Item-Item Collaborative Filtering

Recomienda productos similares según el historial de compras del usuario mediante similitud coseno.

Se utiliza para usuarios con historial reducido.

---

## Market Basket Analysis

Implementado mediante FP-Growth.

Incluye dos modelos independientes:

- Recomendación de productos complementarios.
- Recomendación de pasillos relacionados.

---

## Reorder Prediction

Modelo supervisado encargado de predecir qué productos volverá a comprar un usuario frecuente.

Durante la etapa experimental se evaluaron:

- Random Forest
- LightGBM
- CatBoost
- XGBoost

Finalmente se seleccionó **XGBoost** por obtener el mejor desempeño.

---

# 🚀 API REST

La aplicación expone los siguientes endpoints:

| Método | Endpoint | Descripción |
|---------|----------|-------------|
| GET | / | Estado del servicio |
| GET | /health | Health Check |
| GET | /segment/{user_id} | Segmento del usuario |
| GET | /metrics | Métricas del sistema |
| POST | /recommend | Generar recomendaciones |

---

# 🐳 Deploy

La aplicación se encuentra desplegada en **Render** utilizando **Docker**.

Los modelos entrenados no forman parte del repositorio debido a su tamaño.

Durante el inicio del contenedor se descargan automáticamente desde Google Drive mediante:

```

download_models.py

```

Posteriormente se inicia:

- FastAPI
- Streamlit

Ambos procesos conviven dentro del mismo contenedor utilizando el script:

```

start.sh

```

---

# 💻 Instalación Local

```bash
git clone https://github.com/Caromponce/ProyectoFinal-DataScience-Henry.git

cd ProyectoFinal-DataScience-Henry

pip install -r requirements.txt

python download_models.py

bash start.sh
```

---

# 📈 Resultados

El sistema implementa una arquitectura híbrida basada en cinco estrategias complementarias.

| Estrategia | Segmento objetivo | Objetivo | Estado |
|------------|-------------------|----------|:------:|
| Popularity Baseline | Clientes sin historial | Resolver el problema de Cold Start | ✅ Producción |
| Item-Item Collaborative Filtering | Clientes ocasionales | Recomendar productos similares según historial | ✅ Producción |
| Market Basket Analysis | Carritos con múltiples productos | Recomendar productos complementarios | ✅ Producción |
| Reorder Prediction (XGBoost) | Clientes leales | Predecir la recompra de productos | ✅ Producción |

> **Conclusión:** El principal valor del sistema no reside en un único modelo de Machine Learning, sino en una **arquitectura híbrida** que selecciona automáticamente la estrategia de recomendación más adecuada según el segmento del usuario y el contexto de compra.

---

# 🔮 Futuras Mejoras

- Recomendaciones híbridas con aprendizaje online.
- Actualización incremental de modelos.
- Incorporación de métricas online.
- Monitoreo de modelos mediante MLflow.
- Integración con almacenamiento cloud dedicado.

---

# 👥 Equipo

## Data Horizon

| Integrante | Rol |
|------------|-----|
| Carolina Ponce | Data Scientist |
| Félix Augusto Fernández González | Data Scientist |
| Yael Authier | Data Scientist |
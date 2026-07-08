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
- Market Basket Analysis como módulo transversal de cross-selling mediante FP-Growth.
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

El proyecto implementa una **arquitectura híbrida de recomendación**, donde distintos modelos de Machine Learning trabajan de forma coordinada para ofrecer recomendaciones personalizadas según el perfil y el comportamiento de cada usuario.

A diferencia de un sistema basado en un único algoritmo, la API selecciona automáticamente la estrategia de recomendación más adecuada mediante un flujo compuesto por dos etapas:

1. **Segmentación automática del usuario**, que identifica el tipo de cliente utilizando K-Means junto con reglas de negocio para detectar usuarios nuevos o sin historial suficiente.
2. **Selección dinámica de la estrategia de recomendación**, asignando el modelo más apropiado para cada caso.

El flujo implementado es el siguiente:

```text
Usuario

   │
   ▼
Segmentación automática

   │
   ├── Usuario nuevo o sin historial
   │        ▼
   │  Popularity Baseline
   │
   ├── Cliente Ocasional
   │        ▼
   │  Item-Item Collaborative Filtering
   │
   └── Cliente Leal
            ▼
     Reorder Prediction (XGBoost)

            ▼
   También te puede interesar...
 (Market Basket Analysis)
```

El **Market Basket Analysis** funciona como una capa transversal de **cross-selling**, complementando las recomendaciones principales mediante productos frecuentemente comprados en conjunto.

La solución integra **FastAPI** como backend, **Streamlit** para la interfaz de usuario y **Docker** para el despliegue. Los modelos entrenados se descargan dinámicamente desde Google Drive al iniciar el contenedor desplegado en Render.

---

# ⚙ Stack Tecnológico

## Lenguajes y Análisis de Datos

- Python
- Pandas
- NumPy

## Machine Learning y Experimentación

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
| Reorder Prediction (XGBoost) | Supervisado | Clientes leales | ✅ |

## Popularity Baseline

**Objetivo**

Resolver el problema de Cold Start para usuarios sin historial.

**Entrada**

Usuarios nuevos o sin historial suficiente.

**Salida**

Productos más populares.

---

## Segmentación de Usuarios (K-Means)

La primera etapa del sistema consiste en segmentar automáticamente a los usuarios según su comportamiento de compra. Para ello se utiliza un modelo de **K-Means**, complementado con reglas de negocio que permiten identificar casos donde no existe historial suficiente para aplicar técnicas de recomendación personalizadas.

Los segmentos considerados por el sistema son:

- **Usuarios nuevos** (regla de negocio)
- **Usuarios sin historial suficiente** (regla de negocio)
- **Clientes Ocasionales** (K-Means)
- **Clientes Leales** (K-Means)

La segmentación **no genera recomendaciones por sí misma**, sino que determina qué estrategia de recomendación utilizar en la siguiente etapa del flujo:

- **Popularity Baseline** para usuarios nuevos o sin historial.
- **Item-Item Collaborative Filtering** para clientes ocasionales.
- **Reorder Prediction (XGBoost)** para clientes leales.

---

## Item-Item Collaborative Filtering

Recomienda productos similares según el historial de compras del usuario mediante similitud coseno.

Se utiliza para usuarios con historial reducido.

---

## Market Basket Analysis

El **Market Basket Analysis** fue implementado mediante el algoritmo **FP-Growth** para identificar patrones de compra y asociaciones frecuentes entre productos.

El sistema incluye dos modelos complementarios:

- **Recomendación de productos**, que sugiere artículos frecuentemente comprados en conjunto.
- **Recomendación de pasillos**, que identifica categorías relacionadas para facilitar la exploración de productos.

A diferencia de los demás modelos, **Market Basket Analysis no determina la estrategia principal de recomendación**. Su función es complementar las recomendaciones generadas por el sistema mediante una capa transversal de **cross-selling**, presentada en la aplicación bajo la sección **"También te puede interesar..."**.

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

Los modelos entrenados no forman parte del repositorio debido a su tamaño. Durante el inicio del contenedor se descargan automáticamente desde Google Drive mediante:

```text
download_models.py
```

Posteriormente se inician los siguientes servicios:

- FastAPI
- Streamlit

Ambos procesos conviven dentro del mismo contenedor utilizando el script:

```text
start.sh
```

> **Nota sobre el despliegue**
>
> Debido a las limitaciones de memoria de la versión gratuita de Render, el modelo **Reorder Prediction (XGBoost)** no puede ejecutarse en producción sin superar los recursos disponibles del contenedor. Para la demostración online se implementó un mecanismo de *fallback*, que utiliza predicciones precalculadas generadas con el modelo entrenado y validado localmente.
>
> Esta limitación afecta únicamente al entorno de despliegue y no al desarrollo del proyecto. La arquitectura híbrida, el entrenamiento, la evaluación y la validación del modelo forman parte de la solución implementada.

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

El sistema implementa una **arquitectura híbrida de recomendación**, donde la estrategia utilizada depende automáticamente del perfil y del historial de compras de cada usuario.

| Estrategia | ¿Cuándo se utiliza? | Objetivo | Estado |
|------------|---------------------|----------|:------:|
| Popularity Baseline | Usuarios nuevos o sin historial suficiente | Resolver el problema de Cold Start | ✅ Producción |
| Item-Item Collaborative Filtering | Clientes ocasionales | Recomendar productos similares según el historial de compra | ✅ Producción |
| Reorder Prediction (XGBoost) | Clientes leales | Predecir los productos con mayor probabilidad de recompra | ✅ Producción |
| Market Basket Analysis | Como complemento de las recomendaciones principales | Sugerir productos frecuentemente comprados en conjunto (cross-selling) | ✅ Producción |

> **Conclusión:** El principal valor del sistema no reside en un único modelo de Machine Learning, sino en una **arquitectura híbrida** que combina segmentación, selección automática de estrategias y recomendaciones complementarias para ofrecer una experiencia personalizada según el contexto de cada usuario.

---

# 🔮 Futuras Mejoras

- Ejecución completa del modelo **Reorder Prediction (XGBoost)** en un entorno cloud con mayores recursos de memoria.
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

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos como Proyecto Final del programa Henry Data Science Bootcamp.

El dataset utilizado corresponde al desafío público **Instacart Market Basket Analysis**, disponible para investigación y aprendizaje.
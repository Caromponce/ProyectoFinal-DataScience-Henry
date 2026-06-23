# Proyecto Final — Data Science Henry
## Instacart Market Basket Analysis

Sistema de recomendación de productos construido sobre el dataset público de [Instacart Market Basket Analysis](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis).

---

## Estructura del proyecto

```
ProyectoFinal-DataScience-Henry/
├── data/
│   ├── raw/
│   │   └── instacart/          ← CSVs originales del dataset (no incluidos en el repo)
│   └── processed/              ← Archivos generados por los notebooks
├── notebooks/
│   ├── 01_Data_Understanding.ipynb
│   ├── 02_EDA.ipynb
│   ├── 03_Data_Preprocessing.ipynb
│   ├── 04_Feature_Engineering.ipynb
│   ├── 05_Clustering_Segmentacion.ipynb
│   ├── 06_Market_Basket_Analysis.ipynb
│   ├── 07_Collaborative_Filtering.ipynb
│   └── 08_Reorder_Prediction.ipynb
├── models/                     ← Modelos entrenados (.joblib, .pkl)
├── requirements.txt
└── README.md
```

---

## Configuración inicial

### 1. Clonar el repositorio

```bash
git clone https://github.com/Caromponce/ProyectoFinal-DataScience-Henry.git
cd ProyectoFinal-DataScience-Henry
```

### 2. Descargar el dataset

El dataset **no está incluido** en el repositorio por su tamaño. Descargalo desde [Kaggle — Instacart Market Basket Analysis](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis) y colocá los archivos en `data/raw/instacart/`:

```
data/
└── raw/
    └── instacart/
        ├── aisles.csv
        ├── departments.csv
        ├── orders.csv
        ├── products.csv
        ├── order_products__prior.csv
        └── order_products__train.csv
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar los notebooks en orden

Los notebooks 01–04 preparan los datos. Los notebooks 05–08 son independientes entre sí (excepto que 08 consume artefactos de 05 y 07).

```
notebooks/01_Data_Understanding.ipynb
notebooks/02_EDA.ipynb
notebooks/03_Data_Preprocessing.ipynb
notebooks/04_Feature_Engineering.ipynb

notebooks/05_Clustering_Segmentacion.ipynb
notebooks/06_Market_Basket_Analysis.ipynb
notebooks/07_Collaborative_Filtering.ipynb
notebooks/08_Reorder_Prediction.ipynb
```

---

## Dataset

| Archivo | Filas | Descripción |
|---|---|---|
| `aisles.csv` | 134 | Pasillos del supermercado |
| `departments.csv` | 21 | Departamentos |
| `products.csv` | 49.688 | Catálogo de productos |
| `orders.csv` | 3.421.083 | Pedidos por usuario (día, hora, frecuencia) |
| `order_products__prior.csv` | 32.434.489 | Historial completo de compras |
| `order_products__train.csv` | 1.384.617 | Último pedido de cada usuario (set de entrenamiento) |

---

## Modelos implementados

| Notebook | Modelo | Descripción | Resultado |
|---|---|---|---|
| 05 · Clustering | K-Means (k=3) | Segmentación de usuarios por comportamiento de compra | 3 clusters: ocasional, frecuente leal, explorador |
| 06 · Market Basket | Apriori + FP-Growth | Reglas de asociación a nivel de aisle y producto (top-200) | Reglas con lift > 1 en ambos niveles |
| 07 · Collaborative Filtering | Item-Item Cosine ⭐ + SVD + ALS BM25 | Recomendación basada en patrones colectivos de compra | F1@10 = 0.0176, NDCG@10 = 0.0231 |
| 08 · Reorder Prediction | LightGBM ⭐ + HistGB + LogReg | Predicción binaria de recompra por par (usuario, producto) | PR-AUC = 0.4260, F1 medio por pedido = 0.3819 |

---

## Estado del proyecto

| Notebook | Descripción | Estado |
|---|---|---|
| 01 · Data Understanding | Exploración inicial, estructura y métricas generales | ✅ |
| 02 · EDA | Calidad de datos, comportamiento de usuarios y productos | ✅ |
| 03 · Data Preprocessing | Integración de tablas y filtrado de interacciones | ✅ |
| 04 · Feature Engineering | Features de usuario/producto y muestra para modelado | ✅ |
| 05 · Clustering | Segmentación de usuarios con K-Means | ✅ |
| 06 · Market Basket Analysis | Reglas de asociación Apriori + FP-Growth | ✅ |
| 07 · Collaborative Filtering | Item-Item Cosine + SVD + ALS BM25 | ✅ |
| 08 · Reorder Prediction | Clasificación supervisada LightGBM + HistGB + LogReg | ✅ |

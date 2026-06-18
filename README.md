# Proyecto Final — Data Science Henry
## Instacart Market Basket Analysis

Sistema de recomendación de productos construido sobre el dataset público de [Instacart Market Basket Analysis](https://www.kaggle.com/competitions/instacart-market-basket-analysis/data).



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
│   └── 04_Feature_Engineering.ipynb
├── models/                     ← Modelos entrenados
├── src/                        ← Scripts y utilidades
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

El dataset **no está incluido** en el repositorio por su tamaño. Descargalo desde [Kaggle — Instacart Market Basket Analysis](https://www.kaggle.com/competitions/instacart-market-basket-analysis/data) y colocá los 6 archivos en `data/raw/instacart/`:

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

```
notebooks/01_Data_Understanding.ipynb
notebooks/02_EDA.ipynb
notebooks/03_Data_Preprocessing.ipynb
notebooks/04_Feature_Engineering.ipynb
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

## Estado del proyecto

| Notebook | Descripción | Estado |
|---|---|---|
| 01 · Data Understanding | Exploración inicial, estructura y métricas generales | ✅ |
| 02 · EDA | Calidad de datos, comportamiento de usuarios y productos | ✅ |
| 03 · Data Preprocessing | Integración de tablas y filtrado de interacciones | ✅ |
| 04 · Feature Engineering | Features de usuario/producto y muestra para modelado | ✅ |
| 05 · Modelado | -  | 🔄 En progreso |

---



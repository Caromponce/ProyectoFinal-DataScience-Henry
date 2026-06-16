# Proyecto Final — Data Science Henry
## Instacart Market Basket Analysis

Análisis exploratorio y modelo predictivo sobre el dataset de Instacart Market Basket Analysis.


---

## Estructura del proyecto

```
ProyectoFinal-DataScience-Henry/
├── data/               ← CSVs del dataset (ver instrucciones abajo)
├── src/
│   ├── cargar_datos.py ← función de carga de datos
│   └── EDA.ipynb       ← análisis exploratorio
├── requirements.txt
└── README.md
```

---

## Configuración inicial

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd ProyectoFinal-DataScience-Henry
```

### 2. Crear la carpeta `data` y agregar los CSVs

El dataset **no está incluido** en el repositorio por su tamaño. Descargalo desde [Kaggle — Instacart Market Basket Analysis](https://www.kaggle.com/competitions/instacart-market-basket-analysis/data) y colocá los 6 archivos en la carpeta llamada `data/`:

```
data/
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

### 4. Ejecutar el notebook

Abrí `src/EDA.ipynb` en Jupyter y ejecutá las celdas en orden.

---

## Dataset

| Archivo | Descripción |
|---|---|
| `aisles.csv` | 134 pasillos del supermercado |
| `departments.csv` | 21 departamentos |
| `products.csv` | Catálogo de productos con pasillo y departamento |
| `orders.csv` | Órdenes de cada usuario (día, hora, días desde última compra) |
| `order_products__prior.csv` | Productos del historial de compras |
| `order_products__train.csv` | Productos de la última orden (set de entrenamiento) |

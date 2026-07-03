# Proyecto Final Data Science - Henry

Análisis y modelado sobre el dataset público de [Instacart Market Basket Analysis](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis): segmentación de clientes, sistemas de recomendación de productos y pasillos, y predicción de recompra (reorder).


## Estructura del repositorio

```
ProyectoFinal-DataScience-Henry/
├── data/
│   ├── raw/instacart/        # CSVs originales de Kaggle (no versionados, ver "Descargar el dataset")
│   └── processed/            # Datos intermedios y de salida (catálogos, reglas, métricas en .json/.csv)
├── notebooks/                # Los 10 notebooks del pipeline, numerados en orden de ejecución
├── src/                      # Módulos .py productivos (uno por modelo, listos para importar)
├── models/                   # Artefactos .joblib entrenados 
├── test/                     # Notebook de smoke test de los módulos de src/
├── requirements.txt          # Dependencias del proyecto
└── README.md
```

## Configuración inicial

### 1. Clonar el repositorio

```bash
git clone https://github.com/Caromponce/ProyectoFinal-DataScience-Henry.git
cd ProyectoFinal-DataScience-Henry
```

### 2. Crear entorno e instalar dependencias

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Descargar el dataset

El dataset **no está incluido** en el repositorio por su tamaño (los `.csv`/`.parquet`/`.npz` están en `.gitignore`). Descargalo desde [Kaggle — Instacart Market Basket Analysis](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis) y colocá los archivos en `data/raw/instacart/`:

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

### 4. Ejecutar el pipeline
Ejecutar los notebooks 01 a 10 en orden.


## El dataset

Historial real (anonimizado) de compras online de supermercado, distribuido en 6 tablas relacionadas por IDs de usuario/pedido/producto:

| Tabla | Filas | Descripción |
|-------|------:|-------------|
| `orders.csv` | 3.421.083 | Pedidos de 206.209 usuarios, con día de la semana, hora y días desde el pedido anterior. |
| `products.csv` | 49.688 | Catálogo de productos, cada uno asociado a un pasillo (aisle) y un departamento. |
| `aisles.csv` | 134 | Pasillos/categorías finas de producto. |
| `departments.csv` | 21 | Departamentos, categorías más generales. |
| `order_products__prior.csv` | 32.434.489 | Detalle producto a producto de los pedidos históricos ("prior") de cada usuario. |
| `order_products__train.csv` | 1.384.617 | Detalle del último pedido de cada usuario, usado como etiqueta para entrenar/evaluar. |

Puntos relevantes detectados en el análisis exploratorio (notebooks 01-02): la matriz usuario-producto es muy dispersa (sparsity 99.68%), el 58.97% de las compras son recompras, y la distribución de compras por producto sigue un patrón de "long tail" (pocos productos muy vendidos y una cola larga de productos poco vendidos).

## Modelos implementados

Cada modelo responde a una pregunta de negocio distinta y se guarda como artefacto `.joblib` reutilizable en `models/`, con su módulo importable equivalente en `src/`.

| # | Notebook | Modelo | Descripción |
|---|----------|--------|-------------|
| 05 | `05_Clustering_Segmentacion.ipynb` | **K-Means (segmentación)** | Agrupa usuarios en perfiles de comportamiento de compra (cantidad de pedidos, tamaño de carrito, tasa de recompra, frecuencia) sin etiquetas previas. Resultado: 2 clusters — "Clientes Ocasionales" (56.2%) y "Clientes Leales o frecuentes" (43.8%), Silhouette Score 0.3276. |
| 06 | `06_Popularidad_Baseline.ipynb` | **Popularidad (baseline)** | Recomendador más simple posible: rankea productos por cantidad total de compras históricas. Sirve como piso de comparación y para el problema de cold-start (usuarios sin historial). |
| 07 | `07_Market_Basket_Analysis.ipynb` | **Market Basket Analysis — Producto** | Usa FP-Growth (`mlxtend`) para encontrar reglas de asociación entre productos ("si comprás A, solés comprar B") mediante soporte, confianza y lift. Genera ~1.800 reglas de cross-selling a nivel producto. |
| 08 | `08_Market_Basket_Analysis_Aisles.ipynb` | **Market Basket Analysis — Pasillo** | Misma técnica (FP-Growth) aplicada sobre los 134 pasillos en vez de productos individuales, para detectar relaciones entre categorías más amplias. Genera ~11.000 reglas. |
| 09 | `09_Item_Item_Cosine.ipynb` | **Filtrado colaborativo Item-Item (similitud coseno)** | Calcula similitud coseno entre productos a partir de la matriz usuario-producto, para recomendar productos "parecidos" según qué usuarios los compran juntos. Evaluado con Precision/Recall/MAP y coherencia de categoría (15.6x mejor que el azar). |
| 10 | `10_Reorder_Prediction.ipynb` | **Predicción de recompra (Reorder Prediction)** | Clasificación binaria supervisada: dado un usuario y un producto que ya compró, predice si lo va a volver a comprar en su próximo pedido. Compara XGBoost, LightGBM, CatBoost y RandomForest; gana **XGBoost** (PR-AUC 0.4218, Recall 0.75). |

## Módulos productivos (`src/`)

`src/` contiene la versión importable de cada modelo entrenado (05 a 10), pensada para consumirse desde otro código sin depender de los notebooks ni de los CSV crudos: cada módulo carga su artefacto `.joblib` de `models/` y expone una clase simple con un método de predicción o recomendación.

```python
from popularity_recommender import PopularityRecommender

model = PopularityRecommender.load()
model.recommend(10)
```

`test/test_recommenders.ipynb` sirve como ejemplo de uso y smoke test de los 6 módulos.

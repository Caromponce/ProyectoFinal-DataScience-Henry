"""Recomendador de productos basado en popularidad global (modelo baseline).

Este modulo es la version "productiva" e importable del modelo desarrollado
paso a paso en `notebooks/06_Popularidad_Baseline.ipynb`. La logica es la
misma (ya validada ahi); ese notebook queda con el codigo paso a paso por su
valor didactico, y este modulo es lo que se importa desde otro codigo.

Que es un "baseline de popularidad"
------------------------------------
Es el recomendador mas simple posible: en vez de personalizar la
recomendacion para cada usuario, siempre sugiere los productos que MAS se
compraron en todo el historial (por ejemplo "Banana" o "Bag of Organic
Bananas" en Instacart). No usa nada especifico del usuario.

Sirve principalmente para el problema de "cold-start": cuando un usuario es
nuevo y todavia no tiene historial de compras, no hay forma de personalizar
nada para el, asi que se le muestra el top de productos mas populares como
punto de partida razonable.

No depende de los CSV crudos de Instacart en runtime: todo lo que necesita
(el ranking de productos ya calculado, con nombre y posicion) viene
empaquetado en un unico artefacto `.joblib` autocontenido.

Uso basico
----------
    from popularity_recommender import PopularityRecommender

    model = PopularityRecommender.load()  # busca models/popularity_model.joblib
    model.recommend(10)
    # -> [{'producto': 'Banana', 'rank': 1}, {'producto': 'Bag of Organic Bananas', 'rank': 2}, ...]
"""

from __future__ import annotations

from pathlib import Path

import joblib

# models/popularity_model.joblib, relativo a este archivo (no al cwd de quien importa).
DEFAULT_ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "models" / "popularity_model.joblib"


class PopularityRecommender:
    """Recomienda los productos mas vendidos, igual para cualquier usuario."""

    def __init__(self, ranking_df, metadata=None):
        """
        Parameters
        ----------
        ranking_df : pd.DataFrame
            Debe tener las columnas `product_id`, `product_name`,
            `purchase_count` y `rank`, ya ordenado de mejor (rank=1) a peor.
        metadata : dict o None
            Informacion adicional opcional (por ejemplo fecha de entrenamiento
            o cuantas filas se usaron), solo para trazabilidad.
        """
        self.ranking_df = ranking_df
        self.metadata = metadata or {}

    def recommend(self, n: int = 10) -> list[dict]:
        """Devuelve el top-n de productos mas populares.

        Parameters
        ----------
        n : int
            Cantidad de productos a devolver.

        Returns
        -------
        list[dict]
            `[{'producto': str, 'rank': int}, ...]`, ya ordenado del mejor
            (rank=1) al peor. `rank` es 1-indexado.
        """
        top_n = self.ranking_df.head(n)
        return [
            {"producto": row["product_name"], "rank": int(row["rank"])}
            for _, row in top_n.iterrows()
        ]

    @classmethod
    def load(cls, path: str | Path | None = None) -> "PopularityRecommender":
        """Carga el modelo desde un artefacto `.joblib` autocontenido.

        Parameters
        ----------
        path : str, Path o None
            Ubicacion del artefacto. Si es None, usa
            `models/popularity_model.joblib` resuelto relativo a este
            archivo (funciona sin importar desde donde se ejecute el codigo
            que hace el import).
        """
        artifact_path = Path(path) if path is not None else DEFAULT_ARTIFACT_PATH
        if not artifact_path.exists():
            raise FileNotFoundError(
                f"No se encontro el artefacto del modelo en '{artifact_path}'. "
                "Generalo corriendo notebooks/06_Popularidad_Baseline.ipynb."
            )
        return joblib.load(artifact_path)

    def __repr__(self):
        return f"PopularityRecommender(n_productos={len(self.ranking_df)})"

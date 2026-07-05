"""Predictor de reorder de productos: clasificacion supervisada usuario-producto.

Este modulo es la version "productiva" e importable del modelo desarrollado
paso a paso en `notebooks/10_Reorder_Prediction.ipynb`. La logica de
construccion de features y de prediccion es la misma que se valido ahi; ese
notebook queda con el desarrollo completo (carga de datos, feature
engineering, comparacion de 4 modelos) por su valor didactico, y este modulo
es lo que se importa desde otro codigo para predecir.

A diferencia de los recomendadores no supervisados del proyecto (MBA en
`src/recommender.py`, CF item-item en `src/cf_item_item_recommender.py`),
este modulo es un **clasificador binario**: para cada par (usuario,
producto) que el usuario ya compro alguna vez, predice si lo va a volver a
comprar en su proximo pedido ("si"/"no"), junto con la probabilidad
asociada.

No depende de los CSV crudos de Instacart en runtime: todo lo que necesita
(modelo entrenado, umbral optimo, tablas de features precomputadas de los
usuarios de la muestra de entrenamiento, catalogo de productos) viene
empaquetado en un unico artefacto `.joblib` autocontenido.

Uso basico
----------
    from reorder_predictor import ReorderPredictor

    model = ReorderPredictor.load()  # busca models/reorder_model.joblib por defecto
    model.predict(user_id=123, product_ids=[24852, 47209])
    # -> [{'product_id': 24852, 'product_name': 'Banana', 'reorder': 'si', 'proba': 0.87}, ...]

Usuarios fuera de la muestra de entrenamiento
----------------------------------------------
El artefacto solo trae features precalculadas para los usuarios que se
usaron al entrenar el modelo (ver `metadata['n_users_sample']`). Si se pide
prediccion para un `user_id` fuera de esa muestra (o un `product_id` fuera
del catalogo conocido), las features de usuario/producto/contexto faltantes
se completan con el promedio global de cada feature, y las features de
usuario x producto (que dependen del historial puntual) se completan con 0
(equivalente a "sin historial conocido de esa combinacion"). En ese caso
`predict` imprime una advertencia.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import joblib

# models/reorder_model.joblib, relativo a este archivo (no al cwd de quien importa).
DEFAULT_ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "models" / "reorder_model.joblib"


class ReorderPredictor:
    """Predice si un usuario va a volver a comprar cada producto en su proximo pedido."""

    def __init__(self, artifact: dict):
        self._model = artifact["model"]
        self.model_name: str = artifact["model_name"]
        self._feature_cols: list[str] = artifact["feature_cols"]
        self._threshold: float = artifact["threshold"]

        # Se indexan por sus claves de union una sola vez, aca en el load: asi
        # las busquedas en `predict` (incluso contra `up_features`, que tiene
        # millones de filas) usan el indice hash ya construido en vez de
        # reconstruirlo en cada llamada (eso era ~1000x mas lento).
        self._user_features: pd.DataFrame = artifact["user_features"].set_index("user_id")
        self._product_features: pd.DataFrame = artifact["product_features"].set_index("product_id")
        self._up_features: pd.DataFrame = artifact["up_features"].set_index(["user_id", "product_id"])
        self._target_context: pd.DataFrame = artifact["target_context"].set_index("user_id")

        self._id_to_name: dict = artifact["id_to_name"]
        self.metadata: dict = artifact.get("metadata", {})

        self._known_users = set(self._user_features.index)

        # Promedios globales para completar features de usuarios/productos
        # desconocidos (no vistos durante el entrenamiento de la muestra).
        self._global_means: dict[str, float] = {}
        for tabla in (self._user_features, self._product_features, self._target_context):
            for col in self._feature_cols:
                if col in tabla.columns:
                    self._global_means[col] = float(tabla[col].mean())

    @classmethod
    def load(cls, path: Path | str | None = None) -> "ReorderPredictor":
        """Carga el artefacto entrenado. Sin argumentos busca `models/reorder_model.joblib`."""
        artifact_path = Path(path) if path is not None else DEFAULT_ARTIFACT_PATH
        artifact = joblib.load(artifact_path)
        return cls(artifact)

    def _construir_features(self, user_id: int, product_ids: list[int]) -> pd.DataFrame:
        """Arma la tabla de features para un usuario y una lista de productos.

        Reusa las mismas 4 tablas de features (usuario, producto, usuario x
        producto, contexto del pedido objetivo) que se calcularon en el
        notebook, ya indexadas por sus claves (ver `__init__`). Como `predict`
        siempre recibe un unico usuario, las features de usuario y de contexto
        se buscan una sola vez (no por cada producto); las de producto y de
        usuario x producto se buscan por `reindex`, que reutiliza el indice ya
        construido de esas tablas. Las combinaciones sin historial conocido
        quedan con NaN y se completan en `predict`.
        """
        df = pd.DataFrame({"product_id": product_ids})

        df = df.join(self._product_features, on="product_id")

        for col in self._user_features.columns:
            df[col] = self._user_features[col].get(user_id, np.nan)
        for col in self._target_context.columns:
            df[col] = self._target_context[col].get(user_id, np.nan)

        up_idx = pd.MultiIndex.from_arrays(
            [[user_id] * len(product_ids), product_ids], names=["user_id", "product_id"]
        )
        up_vals = self._up_features.reindex(up_idx).reset_index(drop=True)
        df = pd.concat([df.reset_index(drop=True), up_vals], axis=1)

        return df

    def predict(self, user_id: int, product_ids: int | list[int]) -> list[dict]:
        """Predice reorder ('si'/'no') y probabilidad para cada producto.

        Parameters
        ----------
        user_id : int
            Usuario para el que se quiere predecir.
        product_ids : int o list[int]
            Uno o varios productos (idealmente, productos que el usuario ya
            compro alguna vez; para productos nunca comprados por el usuario
            el modelo no tiene informacion de habito y la prediccion se
            apoya solo en promedios globales).

        Returns
        -------
        list[dict]
            Uno por producto: {'product_id', 'product_name', 'reorder', 'proba'}.
        """
        if isinstance(product_ids, (int, np.integer)):
            product_ids = [int(product_ids)]

        if user_id not in self._known_users:
            print(
                f"Advertencia: user_id={user_id} no estaba en la muestra de entrenamiento "
                f"({self.metadata.get('n_users_sample', '?')} usuarios). Se usan promedios "
                "globales para las features de usuario y de contexto."
            )

        df = self._construir_features(user_id, product_ids)

        # Completar nulos: features de usuario/producto/contexto -> promedio global;
        # features de usuario x producto (historial puntual) -> 0, "sin historial".
        for col in self._feature_cols:
            if col.startswith("up_"):
                df[col] = df[col].fillna(0.0)
            else:
                df[col] = df[col].fillna(self._global_means.get(col, 0.0))

        proba = self._model.predict_proba(df[self._feature_cols])[:, 1]
        df["proba"] = proba
        df["reorder"] = np.where(proba >= self._threshold, "si", "no")
        df["product_name"] = df["product_id"].map(self._id_to_name)

        resultado = df[["product_id", "product_name", "reorder", "proba"]].to_dict(orient="records")
        for r in resultado:
            r["product_id"] = int(r["product_id"])
            r["proba"] = round(float(r["proba"]), 2)
        return resultado

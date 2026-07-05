"""Segmentador de clientes por comportamiento de compra (K-Means).

Este modulo es la version "productiva" e importable del pipeline desarrollado
paso a paso en `notebooks/05_Clustering_Segmentacion.ipynb`. La logica de
preprocesamiento y clustering es la misma que se valido ahi; ese notebook
queda con el desarrollo completo (EDA, comparacion de configuraciones,
seleccion de k, perfiles de cluster) por su valor didactico, y este modulo es
lo que se importa desde otro codigo para clasificar usuarios.

**Rol en el sistema:** K-Means actua como *router*, no como recomendador. Su
salida — `user_id -> nombre de segmento` — es consumida por la capa de
*serving* para decidir que modelo downstream usar (Popularidad, MBA, CF,
Reorder).

Por que las clases de preprocesamiento viven aca (y no solo en el notebook)
------------------------------------------------------------------------------
`SelectiveLog1p` y `Winsorizer` son transformadores custom usados dentro de
un `sklearn.Pipeline`. Si se definen dentro del notebook, quedan atadas al
modulo `__main__` de esa sesion: al persistir el pipeline con joblib y
volver a cargarlo desde otro proceso (por ejemplo, importando este modulo),
la deserializacion falla porque no encuentra `__main__.SelectiveLog1p`.
Definirlas aca, en un modulo real e importable, hace que el pickle sea
estable sin importar desde donde se cargue.

No depende de los CSV crudos de Instacart en runtime: todo lo que necesita
(pipeline de preprocesamiento ya fiteado, modelo K-Means entrenado, mapeo
cluster -> nombre de segmento, y las features precalculadas de los usuarios
que entraron al modelo) viene empaquetado en un unico artefacto `.joblib`
autocontenido.

Uso basico
----------
    from kmeans_segmenter import CustomerSegmenter

    model = CustomerSegmenter.load()  # busca models/kmeans_model.joblib
    model.predict(123)
    # -> 'Clientes Leales o frecuentes'
    model.predict(9_999_999)  # usuario con <5 pedidos o desconocido
    # -> 'Clientes sin historial de compras'

Usuarios sin historial suficiente
----------------------------------
El artefacto solo trae features precalculadas para los usuarios que tuvieron
al menos `min_orders` pedidos (ver metadata del bundle). Cualquier `user_id`
que no aparezca en esa tabla (porque tiene menos pedidos o porque no existe
en el dataset de entrenamiento) recibe la etiqueta
`'Clientes sin historial de compras'`, igual que la regla de negocio del
notebook.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, RobustScaler

# models/kmeans_model.joblib, relativo a este archivo (no al cwd de quien importa).
DEFAULT_ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "models" / "kmeans_model.joblib"

# Etiqueta de negocio para usuarios con pocos pedidos o desconocidos.
SIN_HISTORIAL = "Clientes sin historial de compras"


class SelectiveLog1p(BaseEstimator, TransformerMixin):
    """Aplica log1p solo a las columnas especificadas por sus indices."""

    def __init__(self, col_indices=None):
        self.col_indices = col_indices or []

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = np.asarray(X, dtype=float).copy()
        for j in self.col_indices:
            X[:, j] = np.log1p(X[:, j])
        return X


class Winsorizer(BaseEstimator, TransformerMixin):
    """Recorta cada columna al rango [p_low, p_high] aprendido en fit()."""

    def __init__(self, lower_pct=1, upper_pct=99):
        self.lower_pct = lower_pct
        self.upper_pct = upper_pct

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.lower_caps_ = np.percentile(X, self.lower_pct, axis=0)
        self.upper_caps_ = np.percentile(X, self.upper_pct, axis=0)
        return self

    def transform(self, X, y=None):
        X = np.asarray(X, dtype=float).copy()
        for j in range(X.shape[1]):
            X[:, j] = np.clip(X[:, j], self.lower_caps_[j], self.upper_caps_[j])
        return X


def build_preproc_pipeline(
    feature_names,
    log1p_features,
    use_log1p=True,
    use_winsorize=True,
    scaler_type="standard",
    use_pca=False,
    pca_n_components=0.95,
    random_state=42,
):
    """Devuelve un sklearn.Pipeline serializable que transforma X.

    Misma logica que la funcion homonima desarrollada en el notebook 05: arma
    los pasos de preprocesamiento (log1p selectivo -> winsorizacion ->
    escalado -> PCA opcional) segun la configuracion ganadora.
    """
    steps = []
    log1p_idx = [feature_names.index(f) for f in log1p_features if f in feature_names]

    if use_log1p and log1p_idx:
        steps.append(("log1p", SelectiveLog1p(col_indices=log1p_idx)))

    if use_winsorize:
        steps.append(("winsorize", Winsorizer()))

    scaler = StandardScaler() if scaler_type == "standard" else RobustScaler()
    steps.append(("scaler", scaler))

    if use_pca:
        from sklearn.decomposition import PCA

        steps.append(("pca", PCA(n_components=pca_n_components, random_state=random_state)))

    return Pipeline(steps)


class CustomerSegmenter:
    """Clasifica un usuario en su segmento de negocio a partir de su comportamiento de compra."""

    def __init__(self, artifact: dict):
        self._preproc: Pipeline = artifact["preproc"]
        self._kmeans = artifact["kmeans"]
        self._cluster_to_name: dict = artifact["cluster_to_name"]
        self._feature_names: list[str] = artifact["feature_names"]
        self.min_orders: int = artifact.get("min_orders", 5)
        self.metadata: dict = artifact.get("metadata", {})

        # Features precalculadas (una fila por usuario que entro al modelo,
        # es decir con >= min_orders pedidos), en el mismo orden de columnas
        # que espera el pipeline de preprocesamiento.
        self._user_features: pd.DataFrame = artifact["user_features"][self._feature_names]
        self._known_users = set(self._user_features.index)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "CustomerSegmenter":
        """Carga el artefacto entrenado. Sin argumentos busca `models/kmeans_model.joblib`."""
        artifact_path = Path(path) if path is not None else DEFAULT_ARTIFACT_PATH
        if not artifact_path.exists():
            raise FileNotFoundError(
                f"No se encontro el artefacto del modelo en '{artifact_path}'. "
                "Generalo corriendo notebooks/05_Clustering_Segmentacion.ipynb."
            )
        artifact = joblib.load(artifact_path)
        return cls(artifact)

    def predict(self, user_id: int) -> str:
        """Devuelve el nombre del segmento de negocio para un `user_id`.

        Si el usuario no tiene features precalculadas (menos de
        `self.min_orders` pedidos, o `user_id` desconocido) devuelve
        `SIN_HISTORIAL` sin pasar por el modelo.
        """
        if user_id not in self._known_users:
            return SIN_HISTORIAL

        X_feat = self._user_features.loc[[user_id]].values.astype(float)
        X_tr = self._preproc.transform(X_feat)
        cluster_id = int(self._kmeans.predict(X_tr)[0])
        return self._cluster_to_name[cluster_id]

    def predict_many(self, user_ids: list[int]) -> list[str]:
        """Conveniencia: aplica `predict` a una lista de `user_id`."""
        return [self.predict(uid) for uid in user_ids]

    def __repr__(self):
        return (
            f"CustomerSegmenter(n_usuarios_con_historial={len(self._known_users)}, "
            f"segmentos={sorted(set(self._cluster_to_name.values()))})"
        )

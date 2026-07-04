"""Recomendador de productos basado en filtrado colaborativo item-item (similitud coseno).

Este modulo es la version "productiva" e importable del `recommend_from_cart`
desarrollado paso a paso en `notebooks/09_Item_Item_Cosine.ipynb`. La logica
es la misma (ya validada ahi); ese notebook queda con la funcion inline por su
valor didactico, y este modulo es lo que se importa desde otro codigo.

A diferencia de `src/recommender.py` (que usa reglas de asociacion extraidas
por Market Basket Analysis, es decir "estos productos aparecen juntos en el
mismo pedido"), este modulo mide similitud entre productos a partir de si son
comprados por los mismos usuarios a lo largo de su historial completo. El
score de un producto candidato para un carrito es la suma de sus similitudes
coseno con cada producto del carrito.

No depende de los CSV crudos de Instacart en runtime: todo lo que necesita
(matriz de similitud, mapeos id<->indice, soporte de usuario, nombres de
producto) viene empaquetado en un unico artefacto `.joblib` autocontenido.

Uso basico
----------
    from cf_item_item_recommender import CFItemItemRecommender

    model = CFItemItemRecommender.load()  # busca models/cf_item_item_model.joblib por defecto
    model.recommend([21903, 47209])
    # -> [{'product_id': 24852, 'product_name': 'Banana', 'rank': 1}, ...]
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import joblib

# models/cf_item_item_model.joblib, relativo a este archivo (no al cwd de quien importa).
DEFAULT_ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "models" / "cf_item_item_model.joblib"


class CFItemItemRecommender:
    """Recomienda productos a partir de un carrito, usando similitud coseno item-item pre-calculada."""

    def __init__(
        self,
        similarity_matrix,
        item_to_idx,
        idx_to_item,
        product_support,
        id_to_name,
        max_consequent_support,
        metadata=None,
    ):
        self.similarity_matrix = similarity_matrix
        self.item_to_idx = item_to_idx
        self.idx_to_item = idx_to_item
        self.product_support = product_support
        self.id_to_name = id_to_name
        self.max_consequent_support = max_consequent_support
        self.metadata = metadata or {}

    @classmethod
    def load(cls, path: str | Path | None = None) -> "CFItemItemRecommender":
        """Carga el modelo desde un artefacto `.joblib` autocontenido.

        Parameters
        ----------
        path : str, Path o None
            Ubicacion del artefacto. Si es None, usa `models/cf_item_item_model.joblib`
            resuelto relativo a este archivo (funciona sin importar desde donde
            se ejecute el codigo que hace el import).
        """
        artifact_path = Path(path) if path is not None else DEFAULT_ARTIFACT_PATH
        if not artifact_path.exists():
            raise FileNotFoundError(
                f"No se encontro el artefacto del modelo en '{artifact_path}'. "
                "Genera lo corriendo la seccion 'Exportar artefactos' de "
                "notebooks/09_Item_Item_Cosine.ipynb."
            )
        artifact = joblib.load(artifact_path)
        return cls(
            similarity_matrix=artifact["similarity_matrix"],
            item_to_idx=artifact["item_to_idx"],
            idx_to_item=artifact["idx_to_item"],
            product_support=artifact["product_support"],
            id_to_name=artifact["id_to_name"],
            max_consequent_support=artifact["max_consequent_support"],
            metadata=artifact.get("metadata", {}),
        )

    def recommend(
        self,
        cart_product_ids: list[int],
        top_n: int = 10,
        max_consequent_support: float | None = None,
    ) -> list[dict]:
        """Devuelve una lista de recomendaciones ordenada de mejor a peor.

        Misma logica que `recommend_from_cart` del notebook principal:
        1. Para cada producto candidato, se suma su similitud coseno con cada
           producto del carrito que este en el catalogo del modelo.
        2. Se excluye lo que ya esta en el carrito.
        3. Se excluyen productos con soporte de usuario > `max_consequent_support`
           (politica "no recomendar lo obvio", ver seccion 7 del notebook).
        4. Se ordena por score agregado descendente.

        Productos del carrito que no esten en el catalogo del modelo (soporte
        de usuario insuficiente al momento de entrenar) simplemente no aportan
        score; si ningun producto del carrito esta en el catalogo, se devuelve
        una lista vacia (cold-start).

        Parameters
        ----------
        cart_product_ids : list[int]
            product_id de los productos que ya estan en el carrito.
        top_n : int
            cantidad maxima de recomendaciones a devolver.
        max_consequent_support : float o None
            tope de soporte de usuario para lo que se puede recomendar. Si es
            None, usa el valor guardado en el artefacto. Pasa un valor >= 1.0
            para desactivar este filtro.

        Returns
        -------
        list[dict]
            `[{'product_id': int, 'product_name': str, 'rank': int}, ...]`,
            `rank` 1-indexado (1 = mejor recomendacion). Lista vacia si ningun
            producto del carrito tiene similitudes calculadas (cold-start).
        """
        if max_consequent_support is None:
            max_consequent_support = self.max_consequent_support

        cart_idx = [self.item_to_idx[p] for p in cart_product_ids if p in self.item_to_idx]
        if not cart_idx:
            return []

        cart_set = set(cart_product_ids)
        n_items = self.similarity_matrix.shape[0]
        scores = self.similarity_matrix[cart_idx, :].sum(axis=0)

        candidates = []
        for idx in range(n_items):
            pid = self.idx_to_item[idx]
            if pid in cart_set:
                continue
            score = scores[idx]
            if score <= 0:
                continue
            if self.product_support.get(pid, 0.0) > max_consequent_support:
                continue  # producto demasiado popular, no aporta valor recomendarlo
            candidates.append((score, pid))

        candidates.sort(key=lambda t: t[0], reverse=True)
        candidates = candidates[:top_n]

        return [
            {
                "product_id": int(pid),
                "product_name": self.id_to_name.get(pid, f"?{pid}"),
                "rank": i + 1,
            }
            for i, (_, pid) in enumerate(candidates)
        ]

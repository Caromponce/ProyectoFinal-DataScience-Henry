"""Recomendador de PASILLOS (aisles) basado en reglas de asociacion (Market Basket Analysis).

Este modulo es la version "productiva" e importable del `recommend_from_cart`
desarrollado paso a paso en `notebooks/08_Market_Basket_Analysis_Aisles.ipynb`. La
logica es la misma (ya validada ahi); ese notebook queda con la funcion inline por
su valor didactico, y este modulo es lo que se importa desde otro codigo.

A diferencia de `src/recommender.py` (que recomienda `product_id -> product_id`),
este modulo trabaja a nivel de **pasillo**: las reglas de asociacion son
`aisle_id -> aisle_id`. El carrito de entrada sigue siendo una lista de
`product_id` (lo que el usuario realmente tiene en el carrito); internamente se
traduce cada producto a su pasillo antes de aplicar las reglas.

No depende de los CSV crudos de Instacart en runtime: todo lo que necesita
(reglas, soporte global por pasillo, nombres de pasillo, mapeo producto->pasillo)
viene empaquetado en un unico artefacto `.joblib` autocontenido.

Uso basico
----------
    from mba_aisle_recommender import MBA_Aisle_Recommender

    model = MBA_Aisle_Recommender.load()  # busca models/mba_aisle_recommender.joblib por defecto
    model.recommend([21903, 47209])
    # -> [{'aisle_id': 24, 'aisle_name': 'fresh vegetables', 'rank': 1}, ...]
"""

from __future__ import annotations

from pathlib import Path

import joblib

# models/aisle_recommender.joblib, relativo a este archivo (no al cwd de quien importa).
DEFAULT_ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "models" / "mba_aisle_recommender.joblib"


class MBA_Aisle_Recommender:
    """Recomienda pasillos a partir de un carrito, usando reglas de asociacion pre-entrenadas."""

    def __init__(self, rules, aisle_support, id_to_name, product_to_aisle, max_consequent_support, metadata=None):
        self.rules = rules
        self.aisle_support = aisle_support
        self.id_to_name = id_to_name
        self.product_to_aisle = product_to_aisle
        self.max_consequent_support = max_consequent_support
        self.metadata = metadata or {}

    @classmethod
    def load(cls, path: str | Path | None = None) -> "MBA_Aisle_Recommender":
        """Carga el modelo desde un artefacto `.joblib` autocontenido.

        Parameters
        ----------
        path : str, Path o None
            Ubicacion del artefacto. Si es None, usa `models/mba_aisle_recommender.joblib`
            resuelto relativo a este archivo (funciona sin importar desde donde
            se ejecute el codigo que hace el import).
        """
        artifact_path = Path(path) if path is not None else DEFAULT_ARTIFACT_PATH
        if not artifact_path.exists():
            raise FileNotFoundError(
                f"No se encontro el artefacto del modelo en '{artifact_path}'. "
                "Genera lo corriendo la seccion 'Exportar el modelo' de "
                "notebooks/08_Market_Basket_Analysis_Aisles.ipynb."
            )
        artifact = joblib.load(artifact_path)
        return cls(
            rules=artifact["rules"],
            aisle_support=artifact["aisle_support"],
            id_to_name=artifact["id_to_name"],
            product_to_aisle=artifact["product_to_aisle"],
            max_consequent_support=artifact["max_consequent_support"],
            metadata=artifact.get("metadata", {}),
        )

    def recommend(
        self,
        cart_product_ids: list[int],
        top_n: int = 10,
        max_consequent_support: float | None = None,
    ) -> list[dict]:
        """Devuelve una lista de pasillos recomendados, ordenada de mejor a peor.

        Misma logica que `recommend_from_cart` del notebook principal:
        1. El carrito (product_id) se traduce a los pasillos (aisle_id) que ya
           estan representados en el.
        2. Reglas cuyo antecedente (conjunto de aisle_id) es subconjunto de esos
           pasillos.
        3. Se excluyen pasillos que ya estan representados en el carrito.
        4. Se excluyen pasillos con soporte global > `max_consequent_support`
           (politica "no recomendar lo obvio", ver seccion 7.5 del notebook: evita
           recomendar siempre "fresh fruits"/"fresh vegetables").
        5. Si varias reglas sugieren el mismo pasillo, se queda con la de mejor
           (lift, confidence).
        6. Se ordena por (lift, confidence) descendente.

        Parameters
        ----------
        cart_product_ids : list[int]
            product_id de los productos que ya estan en el carrito (no aisle_id).
        top_n : int
            cantidad maxima de pasillos a devolver.
        max_consequent_support : float o None
            tope de soporte global para lo que se puede recomendar. Si es None,
            usa el valor guardado en el artefacto. Pasa un valor >= 1.0 para
            desactivar este filtro.

        Returns
        -------
        list[dict]
            `[{'aisle_id': int, 'aisle_name': str, 'rank': int}, ...]`, `rank`
            1-indexado (1 = mejor recomendacion). Lista vacia si no hay ninguna
            regla aplicable a ese carrito (cold-start).
        """
        if max_consequent_support is None:
            max_consequent_support = self.max_consequent_support

        cart_aisles = {
            self.product_to_aisle[pid] for pid in cart_product_ids if pid in self.product_to_aisle
        }

        applicable = self.rules[self.rules["antecedents"].apply(lambda a: a.issubset(cart_aisles))]

        best_per_aisle: dict[int, tuple[float, float, int]] = {}
        for _, r in applicable.iterrows():
            for aid in r["consequents"]:
                if aid in cart_aisles:
                    continue  # no recomendamos un pasillo que ya esta representado en el carrito
                if self.aisle_support.get(aid, 0.0) > max_consequent_support:
                    continue  # pasillo demasiado popular, no aporta valor recomendarlo
                candidate = (r["lift"], r["confidence"])
                if aid not in best_per_aisle or candidate > best_per_aisle[aid][:2]:
                    best_per_aisle[aid] = (r["lift"], r["confidence"], aid)

        ranked = sorted(best_per_aisle.values(), key=lambda t: (t[0], t[1]), reverse=True)
        ranked = ranked[:top_n]

        return [
            {
                "aisle_id": aid,
                "aisle_name": self.id_to_name.get(aid, f"?{aid}"),
                "rank": i + 1,
            }
            for i, (_, _, aid) in enumerate(ranked)
        ]

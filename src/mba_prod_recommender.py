"""Recomendador de productos basado en reglas de asociacion (Market Basket Analysis).

Este modulo es la version "productiva" e importable del `recommend_from_cart`
desarrollado paso a paso en `notebooks/07_Market_Basket_Analysis.ipynb`. La logica
es la misma (ya validada ahi); ese notebook queda con la funcion inline por su
valor didactico, y este modulo es lo que se importa desde otro codigo.

No depende de los CSV crudos de Instacart en runtime: todo lo que necesita
(reglas, soporte global por producto, nombres de producto) viene empaquetado
en un unico artefacto `.joblib` autocontenido (ver `models/README.md`).

Uso basico
----------
    from recommender import Recommender

    model = Recommender.load()  # busca models/mba_prod_recommender.joblib por defecto
    model.recommend([21903, 47209])
    # -> [{'product_id': 30391, 'product_name': 'Organic Cucumber', 'rank': 1}, ...]
"""

from __future__ import annotations

from pathlib import Path

import joblib

# models/recommender.joblib, relativo a este archivo (no al cwd de quien importa).
DEFAULT_ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "models" / "mba_prod_recommender.joblib"


class MBA_Prod_Recommender:
    """Recomienda productos a partir de un carrito, usando reglas de asociacion pre-entrenadas."""

    def __init__(self, rules, product_support, id_to_name, max_consequent_support, metadata=None):
        self.rules = rules
        self.product_support = product_support
        self.id_to_name = id_to_name
        self.max_consequent_support = max_consequent_support
        self.metadata = metadata or {}

    @classmethod
    def load(cls, path: str | Path | None = None) -> "MBA_Prod_Recommender":
        """Carga el modelo desde un artefacto `.joblib` autocontenido.

        Parameters
        ----------
        path : str, Path o None
            Ubicacion del artefacto. Si es None, usa `models/recommender.joblib`
            resuelto relativo a este archivo (funciona sin importar desde donde
            se ejecute el codigo que hace el import).
        """
        artifact_path = Path(path) if path is not None else DEFAULT_ARTIFACT_PATH
        if not artifact_path.exists():
            raise FileNotFoundError(
                f"No se encontro el artefacto del modelo en '{artifact_path}'. "
                "Genera lo corriendo la seccion 'Exportar el modelo' de "
                "notebooks/07_Market_Basket_Analysis.ipynb."
            )
        artifact = joblib.load(artifact_path)
        return cls(
            rules=artifact["rules"],
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
        1. Reglas cuyo antecedente es subconjunto del carrito.
        2. Se excluye lo que ya esta en el carrito.
        3. Se excluyen productos con soporte global > `max_consequent_support`
           (politica "no recomendar lo obvio", ver seccion 7.5 del notebook).
        4. Si varias reglas sugieren el mismo producto, se queda con la de
           mejor (lift, confidence).
        5. Se ordena por (lift, confidence) descendente.

        Parameters
        ----------
        cart_product_ids : list[int]
            product_id de los productos que ya estan en el carrito.
        top_n : int
            cantidad maxima de recomendaciones a devolver.
        max_consequent_support : float o None
            tope de soporte global para lo que se puede recomendar. Si es None,
            usa el valor guardado en el artefacto (por defecto 0.10). Pasa un
            valor >= 1.0 para desactivar este filtro.

        Returns
        -------
        list[dict]
            `[{'product_id': int, 'product_name': str, 'rank': int}, ...]`,
            `rank` 1-indexado (1 = mejor recomendacion). Lista vacia si no hay
            ninguna regla aplicable a ese carrito (cold-start).
        """
        if max_consequent_support is None:
            max_consequent_support = self.max_consequent_support

        cart = set(cart_product_ids)
        applicable = self.rules[self.rules["antecedents"].apply(lambda a: a.issubset(cart))]

        best_per_product: dict[int, tuple[float, float, int]] = {}
        for _, r in applicable.iterrows():
            for pid in r["consequents"]:
                if pid in cart:
                    continue  # no recomendamos algo que ya esta en el carrito
                if self.product_support.get(pid, 0.0) > max_consequent_support:
                    continue  # producto demasiado popular, no aporta valor recomendarlo
                candidate = (r["lift"], r["confidence"])
                if pid not in best_per_product or candidate > best_per_product[pid][:2]:
                    best_per_product[pid] = (r["lift"], r["confidence"], pid)

        ranked = sorted(best_per_product.values(), key=lambda t: (t[0], t[1]), reverse=True)
        ranked = ranked[:top_n]

        return [
            {
                "product_id": pid,
                "product_name": self.id_to_name.get(pid, f"?{pid}"),
                "rank": i + 1,
            }
            for i, (_, _, pid) in enumerate(ranked)
        ]

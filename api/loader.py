from pathlib import Path
import sys
import subprocess
import os

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
MODELS_DIR = ROOT_DIR / "models"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

# Garantiza que los modelos existan antes de que FastAPI intente cargarlos
subprocess.run(["python", str(ROOT_DIR / "download_models.py")], check=True)

print("Modelos verificados desde api.loader:")
print(os.listdir(MODELS_DIR))

from kmeans_segmenter import CustomerSegmenter
from popularity_recommender import PopularityRecommender
from mba_prod_recommender import MBA_Prod_Recommender
from mba_aisle_recommender import MBA_Aisle_Recommender
from cf_item_item_recommender import CFItemItemRecommender
from reorder_predictor import ReorderPredictor


class ModelLoader:
    def __init__(self):
        self._segmenter = None
        self._popularity = None
        self._mba_products = None
        self._mba_aisles = None
        self._item_item = None
        self._reorder = None

    @property
    def segmenter(self):
        if self._segmenter is None:
            self._segmenter = CustomerSegmenter.load()
        return self._segmenter

    @property
    def popularity(self):
        if self._popularity is None:
            self._popularity = PopularityRecommender.load()
        return self._popularity

    @property
    def mba_products(self):
        if self._mba_products is None:
            self._mba_products = MBA_Prod_Recommender.load()
        return self._mba_products

    @property
    def mba_aisles(self):
        if self._mba_aisles is None:
            self._mba_aisles = MBA_Aisle_Recommender.load()
        return self._mba_aisles

    @property
    def item_item(self):
        if self._item_item is None:
            self._item_item = CFItemItemRecommender.load()
        return self._item_item

    @property
    def reorder(self):
        if self._reorder is None:
            self._reorder = ReorderPredictor.load()
        return self._reorder


models = ModelLoader()
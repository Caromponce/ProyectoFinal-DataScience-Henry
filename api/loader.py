from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from kmeans_segmenter import CustomerSegmenter
from popularity_recommender import PopularityRecommender
from mba_prod_recommender import MBA_Prod_Recommender
from mba_aisle_recommender import MBA_Aisle_Recommender
from cf_item_item_recommender import CFItemItemRecommender
from reorder_predictor import ReorderPredictor


class ModelLoader:
    def __init__(self):
        self.segmenter = CustomerSegmenter.load()
        self.popularity = PopularityRecommender.load()
        self.mba_products = MBA_Prod_Recommender.load()
        self.mba_aisles = MBA_Aisle_Recommender.load()
        self.item_item = CFItemItemRecommender.load()
        self.reorder = ReorderPredictor.load()


models = ModelLoader()
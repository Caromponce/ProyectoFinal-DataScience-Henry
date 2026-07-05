import os
import gdown

MODELS_DIR = "models"
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1-ur31Pnxf2wqxTskS9GSKHLeJWGBAEOT?usp=sharing"

EXPECTED_MODELS = [
    "cf_item_item_model.joblib",
    "kmeans_model.joblib",
    "mba_aisle_recommender.joblib",
    "mba_prod_recommender.joblib",
    "popularity_model.joblib",
    "reorder_model.joblib",
]

os.makedirs(MODELS_DIR, exist_ok=True)

missing_models = [
    model for model in EXPECTED_MODELS
    if not os.path.exists(os.path.join(MODELS_DIR, model))
]

if missing_models:
    print("Descargando modelos desde Google Drive...")
    gdown.download_folder(
        DRIVE_FOLDER_URL,
        output=MODELS_DIR,
        quiet=False,
        use_cookies=False
    )
else:
    print("Los modelos ya existen. No se descargan nuevamente.")

for model in EXPECTED_MODELS:
    path = os.path.join(MODELS_DIR, model)
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el modelo requerido: {path}")

print("Modelos disponibles correctamente.")
import os
import time
import gdown

MODELS_DIR = "models"

MODELS = {
    "cf_item_item_model.joblib": "1FrBsKOxrf5YScofFkHCC62GD9gUspch3",
    "kmeans_model.joblib": "1yHXnS5oIt5D0fYc5vo3UGdcmJSnySm2J",
    "mba_aisle_recommender.joblib": "1bi0bKFTa1AtSIEYOGne6Mp15pBygKphU",
    "mba_prod_recommender.joblib": "1HQBbQNVqMq82RiB25w3hE3Lp2iNKnU5N",
    "popularity_model.joblib": "1IX93S1F1Z8LSZgQC3vrAqcQtee1ogo-Y",
    "reorder_model.joblib": "1cta7FL29qzUsh2-FRtL1SehNjRisu-vU",
}

os.makedirs(MODELS_DIR, exist_ok=True)

def download_model(filename, file_id, retries=3):
    output_path = os.path.join(MODELS_DIR, filename)

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"Modelo ya existente: {filename}")
        return

    url = f"https://drive.google.com/uc?id={file_id}"

    for attempt in range(1, retries + 1):
        try:
            print(f"Descargando modelo: {filename} | intento {attempt}/{retries}")

            gdown.download(
                url=url,
                output=output_path,
                quiet=False,
            )

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"Modelo descargado correctamente: {filename}")
                return

        except Exception as e:
            print(f"Error descargando {filename}: {e}")

        time.sleep(5)

    raise FileNotFoundError(f"No se pudo descargar el modelo requerido: {filename}")

for filename, file_id in MODELS.items():
    download_model(filename, file_id)

print("Todos los modelos están disponibles correctamente.")
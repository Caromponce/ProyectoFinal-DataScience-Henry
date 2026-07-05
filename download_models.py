import os
import gdown

MODELS_DIR = "models"
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1-ur31Pnxf2wqxTskS9GSKHLeJWGBAEOT?usp=sharing"

os.makedirs(MODELS_DIR, exist_ok=True)

print("Descargando modelos desde Google Drive...")

gdown.download_folder(
    DRIVE_FOLDER_URL,
    output=MODELS_DIR,
    quiet=False,
    use_cookies=False
)

print("Modelos descargados correctamente.")
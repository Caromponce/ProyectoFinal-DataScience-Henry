from PIL import Image
import os

files = [
    "assets/architecture.png",
    "assets/banner_data_horizon.png",
    "assets/favicon.png",
    "assets/logo_data_horizon.png",
]

for f in files:
    img = Image.open(f).convert("RGBA")
    img.thumbnail((1200, 1200))
    img.save(f, optimize=True)
    print(f, os.path.getsize(f))
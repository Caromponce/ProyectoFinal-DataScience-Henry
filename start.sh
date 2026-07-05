#!/bin/bash

python download_models.py

python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 &

streamlit run app/Inicio.py \
  --server.port ${PORT:-7860} \
  --server.address 0.0.0.0
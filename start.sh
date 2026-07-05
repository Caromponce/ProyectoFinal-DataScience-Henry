#!/bin/bash

python download_models.py

python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 &

streamlit run app/🏠_Inicio.py \
  --server.port 7860 \
  --server.address 0.0.0.0
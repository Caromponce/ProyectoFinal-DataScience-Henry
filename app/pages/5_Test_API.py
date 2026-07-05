import streamlit as st
import requests
import os

st.title("Test FastAPI")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.write("API_URL:", API_URL)

if st.button("Probar /health"):
    r = requests.get(f"{API_URL}/health", timeout=30)
    st.write(r.status_code)
    st.json(r.json())

if st.button("Probar /segment/1"):
    r = requests.get(f"{API_URL}/segment/1", timeout=30)
    st.write(r.status_code)
    st.text(r.text)

if st.button("Probar /recommend"):
    payload = {
        "user_id": 1,
        "product_ids": [21903, 47209],
        "n": 5
    }
    r = requests.post(f"{API_URL}/recommend", json=payload, timeout=60)
    st.write(r.status_code)
    st.text(r.text)
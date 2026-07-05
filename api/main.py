from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Instacart Recommendation API",
    version="1.0.0",
    description="Backend para el sistema de recomendación de Instacart"
)

app.include_router(router)
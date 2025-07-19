from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import scan  # Importa el router desde app/routers/scan.py

app = FastAPI(
    title="Auditor Docker/K8s",
    description="API para analizar configuraciones de Docker y Kubernetes",
    version="0.1.0"
)

# Middleware CORS para permitir conexión desde React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API Auditor Docker/K8s"}

# Incluir rutas del archivo scan.py
app.include_router(scan.router)


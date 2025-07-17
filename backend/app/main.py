from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Auditor Docker/K8s",
    description="API para analizar configuraciones de Docker y Kubernetes",
    version="0.1.0"
)

# CORS para frontend local
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

@app.post("/scan/")
async def scan_config(file: UploadFile = File(...)):
    # Aquí más adelante llamarás a hadolint, trivy, kube-linter, etc.
    filename = file.filename
    content = await file.read()
    return {
        "filename": filename,
        "status": "Análisis pendiente",
        "lines": len(content.decode().splitlines())
    }

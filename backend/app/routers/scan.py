from fastapi import APIRouter, UploadFile, File
import subprocess
import tempfile
import os
import json
import re
from app.utils.parsers import (
    normalize_hadolint,
    normalize_trivy,
    normalize_kubelinter,
    normalize_dclint,
)
from app.utils.suggestions import (
    suggest_remediations_dockerfile,
    suggest_remediations_docker_compose,
    suggest_remediations_kubernetes_yaml
)

from app.utils.storage import save_result

router = APIRouter()

def extract_image_name(filename: str, content: str) -> str | None:
    """
    Extrae el nombre de la imagen desde el contenido del archivo, 
    según del tipo que sea.

    Args:
    -----------
    filename : str
        Nombre del archivo subido.
    content : str
        Contenido del archivo.

    Returns:
    --------
    str | None
        El nombre de la imagen encontrada, o None si no se ha detectado.
    """

    if "Dockerfile" in filename:
        match = re.search(r'^FROM\s+([\w\-./:]+)', content, re.MULTILINE)
    elif filename.endswith(".yaml") or filename.endswith(".yml") or "compose" in filename:
        match = re.search(r'image:\s*"?([\w\-./:]+)"?', content)
    else:
        match = None
    return match.group(1) if match else None

@router.post("/scan/")
async def scan_file(file: UploadFile = File(...)):
    """
    Endpoint principal de análisis de archivos.

    Flujo:
    ------
    1. Guarda el archivo.
    2. Detecta el tipo de archivo (Dockerfile, docker-compose o manifiesto de Kubernetes).
    3. Ejecuta la herramienta de análisis correspondiente:
        - hadolint (Dockerfile)
        - dclint (docker-compose.yaml)
        - kube-linter (manifiestos Kubernetes)
    4. Si hay imagen asociada, ejecuta trivy para detectar vulnerabilidades.
    5. Estandariza resultados.
    6. Genera una versión remediada.
    7. Devuelve resultados y sugerencias.

    Returns:
    --------
    dict
        Contiene:
        - filename
        - original_content
        - tools_run
        - results
        - normalized_findings
        - suggested_content (archivo modificado con buenas prácticas)
    """

    filename = file.filename
    suffix = os.path.splitext(filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()

        decoded_content = content.decode()
        results = {}

        if "Dockerfile" in filename or filename.endswith(".Dockerfile"):
            output = subprocess.run(
                ["hadolint", "--format", "json", tmp.name],
                capture_output=True, text=True
            )
            try:
                results["hadolint"] = json.loads(output.stdout)
            except json.JSONDecodeError:
                results["hadolint"] = {"error": "Error parsing hadolint output"}

        elif "docker-compose" in filename or filename.endswith("compose.yaml"):
            output = subprocess.run(
                ["dclint", "-f", "json", tmp.name],
                capture_output=True, text=True
            )
            try:
                results["dclint"] = json.loads(output.stdout)
            except json.JSONDecodeError:
                results["dclint"] = {"error": "Error parsing dclint output"}

        elif filename.endswith(".yaml") or filename.endswith(".yml"):
            output = subprocess.run(
                ["kube-linter", "lint", "--format", "json", tmp.name],
                capture_output=True, text=True
            )
            try:
                results["kube-linter"] = json.loads(output.stdout)
            except json.JSONDecodeError:
                results["kube-linter"] = {"error": "Error parsing kube-linter output"}

        image = extract_image_name(filename, decoded_content)
        if image:
            output = subprocess.run(
                ["trivy", "image", "--quiet", "--format", "json", image],
                capture_output=True, text=True
            )
            try:
                trivy_data = json.loads(output.stdout)
                trivy_findings = []
                for target in trivy_data.get("Results", []):
                    for vuln in target.get("Vulnerabilities", []):
                        trivy_findings.append({
                            "VulnerabilityID": vuln.get("VulnerabilityID"),
                            "PkgName": vuln.get("PkgName"),
                            "InstalledVersion": vuln.get("InstalledVersion"),
                            "FixedVersion": vuln.get("FixedVersion"),
                            "Severity": vuln.get("Severity"),
                            "Title": vuln.get("Title"),
                            "Description": vuln.get("Description", "")[:200]
                        })
                results["trivy"] = trivy_findings
            except json.JSONDecodeError:
                results["trivy"] = {"error": "Error parsing trivy output"}

        os.unlink(tmp.name)

        normalized = []
        if "hadolint" in results and isinstance(results["hadolint"], list):
            normalized += normalize_hadolint(results["hadolint"], filename)
        if "trivy" in results and isinstance(results["trivy"], list):
            normalized += normalize_trivy(results["trivy"], filename)
        if "kube-linter" in results and isinstance(results["kube-linter"], dict):
            normalized += normalize_kubelinter(results["kube-linter"], filename)
        if "dclint" in results and isinstance(results["dclint"], list):
            normalized += normalize_dclint(results["dclint"], filename)

        if "Dockerfile" in filename or filename.endswith(".Dockerfile"):
            suggested_content = suggest_remediations_dockerfile(decoded_content)
        elif "docker-compose" in filename or filename.endswith("compose.yaml"):
            suggested_content = suggest_remediations_docker_compose(decoded_content)
        elif filename.endswith(".yaml") or filename.endswith(".yml"):
            suggested_content = suggest_remediations_kubernetes_yaml(decoded_content)
        else:
            suggested_content = ""

        save_result({
            "filename": filename,
            "original_content": decoded_content,
            "suggested_content": suggested_content,
            "tools_run": list(results.keys()),
            "results": results,
            "normalized_findings": normalized
        })

        return {
            "filename": filename,
            "original_content": decoded_content,
            "tools_run": list(results.keys()),
            "results": results,
            "normalized_findings": normalized,
            "suggested_content": suggested_content
        }
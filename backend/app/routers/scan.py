from fastapi import APIRouter, UploadFile, File
import subprocess
import tempfile
import os
import json
import re

router = APIRouter()

def extract_image_name(filename: str, content: str) -> str | None:
    if "Dockerfile" in filename:
        match = re.search(r'^FROM\s+([\w\-./:]+)', content, re.MULTILINE)
    elif filename.endswith(".yaml") or filename.endswith(".yml") or "compose" in filename:
        match = re.search(r'image:\s*"?([\w\-./:]+)"?', content)
    else:
        match = None
    return match.group(1) if match else None

@router.post("/scan/")
async def scan_file(file: UploadFile = File(...)):
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
                ["dclint", "--formatter", "json", tmp.name],
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

        # --- TRIVY (extrae imagen del contenido del archivo y escanea) ---
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

        return {
            "filename": filename,
            "tools_run": list(results.keys()),
            "results": results
        }
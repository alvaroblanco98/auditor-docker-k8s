from fastapi import APIRouter, UploadFile, File
import subprocess
import tempfile
import os
import json

router = APIRouter()

@router.post("/scan/")
async def scan_file(file: UploadFile = File(...)):
    filename = file.filename
    suffix = os.path.splitext(filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()

        results = {}

        if "Dockerfile" in filename or filename.endswith(".Dockerfile"):
            output = subprocess.run(
                ["hadolint", "-f", "json", tmp.name],
                capture_output=True, text=True
            )
            try:
                results["hadolint"] = json.loads(output.stdout)
            except json.JSONDecodeError:
                results["hadolint"] = {"error": "Error parsing hadolint output"}

        elif "docker-compose" in filename or filename.endswith("compose.yaml"):
            output = subprocess.run(
                ["trivy", "-c", "-f", "json", tmp.name],
                capture_output=True, text=True
            )
            try:
                results["hadolint"] = json.loads(output.stdout)
            except json.JSONDecodeError:
                results["hadolint"] = {"error": "Error parsing hadolint output"}

        elif filename.endswith(".yaml") or filename.endswith(".yml"):
            output = subprocess.run(
                ["kube-linter", "lint", "--format", "json", tmp.name],
                capture_output=True, text=True
            )
            try:
                results["kube-linter"] = json.loads(output.stdout)
            except json.JSONDecodeError:
                results["kube-linter"] = {"error": "Error parsing kube-linter output"}

        os.unlink(tmp.name)

        return {
            "filename": filename,
            "tools_run": list(results.keys()),
            "results": results
        }
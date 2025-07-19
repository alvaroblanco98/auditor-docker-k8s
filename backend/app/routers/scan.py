from fastapi import APIRouter, UploadFile, File
import subprocess
import tempfile
import os

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
            output = subprocess.run(["hadolint", tmp.name], capture_output=True, text=True)
            results["hadolint"] = output.stdout.strip()
        elif filename.endswith(".yaml") or filename.endswith(".yml"):
            output = subprocess.run(["kube-linter", "lint", tmp.name], capture_output=True, text=True)
            results["kube-linter"] = output.stdout.strip()

        os.unlink(tmp.name)
        return {
            "filename": filename,
            "tools_run": list(results.keys()),
            "results": results
        }

def normalize_hadolint(data: list, filename: str) -> list:
    if not isinstance(data, list):
        return []

    return [
        {
            "tool": "hadolint",
            "file": filename,
            "rule": item.get("code"),
            "severity": item.get("level"),
            "message": item.get("message"),
            "line": item.get("line"),
            "fix": None
        }
        for item in data
    ]


def normalize_trivy(data: list, filename: str) -> list:
    if not isinstance(data, list):
        return []

    return [
        {
            "tool": "trivy",
            "file": filename,
            "rule": item.get("VulnerabilityID"),
            "severity": item.get("Severity"),
            "message": item.get("Title"),
            "line": None,
            "fix": item.get("FixedVersion")
        }
        for item in data
    ]


def normalize_kubelinter(data: dict, filename: str) -> list:
    if not isinstance(data, dict):
        return []

    findings = []
    for report in data.get("Reports", []):
        findings.append({
            "tool": "kube-linter",
            "file": report.get("Object", {}).get("Metadata", {}).get("FilePath", filename),
            "rule": report.get("Check"),
            "severity": "danger",  # puedes ajustar según criticidad si se añade
            "message": report.get("Diagnostic", {}).get("Message"),
            "line": None,
            "fix": report.get("Remediation")
        })
    return findings


def normalize_dclint(data: list, filename: str) -> list:
    if not isinstance(data, list):
        return []

    findings = []
    for file_result in data:
        file_path = file_result.get("filePath", filename)
        for msg in file_result.get("messages", []):
            findings.append({
                "tool": "dclint",
                "file": file_path,
                "rule": msg.get("rule"),
                "severity": msg.get("severity"),
                "message": msg.get("message"),
                "line": msg.get("line"),
                "fix": msg.get("meta", {}).get("description")
            })
    return findings
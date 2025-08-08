""""
parsers.py

Este módulo contiene funciones de normalización de resultados
de diferentes herramientas de análisis (Hadolint, Trivy, Kube-linter, DClint)
a un formato común.

Formato normalizado:
{
    "tool": str,        # Nombre de la herramienta que generó el hallazgo
    "file": str,        # Nombre del archivo analizado
    "rule": str,        # Regla o identificador de la vulnerabilidad
    "severity": str,    # Severidad (critical, high, medium, low, etc.)
    "message": str,     # Mensaje o descripción del hallazgo
    "line": int | None, # Número de línea si aplica
    "fix": str | None   # Sugerencia de remediación o versión corregida
}
"""

def normalize_hadolint(data: list, filename: str) -> list:
    """
    Estandariza la salida de Hadolint a un formato común.

    Args:
        data (list): Lista con la salida JSON de Hadolint.
        filename (str): Nombre del archivo analizado.

    Returns:
        list: Lista de resultados normalizados.
    """

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
    """
    Normaliza la salida de Trivy a un formato común.

    Args:
        data (list): Lista con vulnerabilidades detectadas por trivy.
        filename (str): Nombre del archivo o imagen analizada.

    Returns:
        list: Lista de resultados normalizados.
    """
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
    """
    Estandariza la salida de Kube-linter a un formato común.

    Args:
        data (dict): Diccionario con el resultado JSON de kube-linter.
        filename (str): Nombre del archivo analizado.

    Returns:
        list: Lista de resultados normalizados.
    """

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
    """
    Estandariza la salida de DClint a un formato común.

    Args:
        data (list): Lista con la salida JSON de dclint.
        filename (str): Nombre del archivo analizado.

    Returns:
        list: Lista de resultados normalizados.
    """
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
import json
import os
from datetime import datetime, timezone

DB_PATH = "results.json"

def load_all_results():
    """
    Carga todos los resultados almacenados en el archivo JSON.

    Returns:
    --------
    Lista de diccionarios con los resultados previos.
    Si el archivo no existe, retorna una lista vacía.
    """
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_result(entry: dict):
    """
    Guarda un nuevo resultado de análisis en un archivo JSON.

    Parámetros:
    -----------
    entry : dict
        Diccionario que contiene la información del análisis.
        Debe incluir campos como filename, tools_run, results, suggested_content, etc.

    Lógica:
    -------
    1. Carga todos los resultados existentes con load_all_results().
    2. Añade un diccionario que incluye:
        - id: número secuencial del análisis (basado en la longitud actual de la lista).
        - timestamp: fecha y hora actual en UTC.
        - **entry: todos los datos recibidos en la entrada.
    3. Sobrescribe el archivo results.json con la nueva lista de resultados.
    """

    data = load_all_results()
    data.append({
        "id": len(data) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **entry
    })
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

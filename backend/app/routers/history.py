from fastapi import APIRouter
from app.utils.storage import load_all_results

router = APIRouter()

@router.get("/history/")
def get_history():
    """

    Functionality:
    ---------------
    Devuelve el historial de análisis previos que han sido guardados en el sistema.

    Logic:
    -------
    - Llama a la función load_all_results() del módulo app.utils.storage
      para cargar todos los resultados almacenados.
    - Calcula la cantidad total de análisis guardados.
    - Devuelve un JSON con:
        - count: número de resultados encontrados.
        - history: lista con todos los resultados previos.
    """

    results = load_all_results()
    return {
        "count": len(results),
        "history": results
    }

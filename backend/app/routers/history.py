from fastapi import APIRouter
from app.utils.storage import load_all_results

router = APIRouter()

@router.get("/history/")
def get_history():
    results = load_all_results()
    return {
        "count": len(results),
        "history": results
    }

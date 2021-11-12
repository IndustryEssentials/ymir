from typing import Dict, List

from fastapi import APIRouter, Depends

from app.api import deps
from app.schemas import KeywordOut
from app.utils.class_ids import CLASS_TYPES

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(deps.get_current_active_user)],
    response_model=KeywordOut,
)
def get_keywords() -> Dict:
    """
    get keywords list,
    aka class_names
    """
    return {"result": list(CLASS_TYPES.values())}

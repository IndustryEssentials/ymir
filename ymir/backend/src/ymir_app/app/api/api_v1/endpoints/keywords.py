from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.logger import logger

from app import models
from app.api import deps
from app.config import settings
from app.schemas.keyword import (
    KeywordsCreateOut,
    KeywordsPaginationOut,
    KeywordUpdate,
    KeywordsInput,
    KeywordsCheckDupOut,
)
from app.utils.cache import CacheClient
from app.utils.ymir_controller import ControllerClient
from app.libs.common import pagination
from app.libs.labels import upsert_labels
from common_utils.labels import SingleLabel, UserLabels

router = APIRouter()


@router.get(
    "/",
    response_model=KeywordsPaginationOut,
)
def get_keywords(
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
    q: Optional[str] = Query(None, description="query keywords"),
    offset: int = Query(0),
    limit: Optional[int] = Query(None),
) -> Dict:
    """
    Get keywords and aliases
    """
    try:
        items = list(user_labels.filter_labels(q))
    except KeyError:
        logger.info("found no keywords for query: %s", q)
        items = []
    if settings.REVERSE_KEYWORDS_OUTPUT:
        items.reverse()

    res = {"total": len(items), "items": pagination(items, offset, limit)}
    return {"result": res}


@router.post("/", response_model=KeywordsCreateOut)
def create_keywords(
    *,
    keywords_input: KeywordsInput,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    cache: CacheClient = Depends(deps.get_cache),
) -> Any:
    """
    Batch create given keywords and aliases to keywords list
    """
    new_labels = UserLabels(labels=keywords_input.keywords)
    result = upsert_labels(
        user_id=current_user.id,
        new_labels=new_labels,
        controller_client=controller_client,
    )
    cache.delete_personal_keywords_cache()
    return {"result": result}


@router.post("/check_duplication", response_model=KeywordsCheckDupOut)
def check_keywords_duplication(
    *,
    keywords_input: KeywordsInput,
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    dups = user_labels.find_dups([single_label.name for single_label in keywords_input.keywords])
    return {"result": dups}


@router.patch(
    "/{keyword}",
    response_model=KeywordsCreateOut,
)
def update_keyword_aliases(
    *,
    keyword: str,
    aliases_in: KeywordUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    cache: CacheClient = Depends(deps.get_cache),
) -> Any:
    updated_label = SingleLabel(name=keyword, aliases=aliases_in.aliases)
    new_labels = UserLabels(labels=[updated_label])
    result = upsert_labels(
        user_id=current_user.id,
        new_labels=new_labels,
        controller_client=controller_client,
    )
    cache.delete_personal_keywords_cache()
    return {"result": result}

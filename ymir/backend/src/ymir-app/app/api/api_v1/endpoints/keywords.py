from functools import partial
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.logger import logger

from app import models
from app.api import deps
from app.config import settings
from app.schemas import (
    Keyword,
    KeywordsCreate,
    KeywordsCreateOut,
    KeywordsPaginationOut,
    KeywordUpdate,
)
from app.utils.cache import CacheClient
from app.utils.class_ids import (
    find_duplication_in_labels,
    keywords_to_labels,
    labels_to_keywords,
)
from app.utils.ymir_controller import ControllerClient

router = APIRouter()


@router.get(
    "/",
    response_model=KeywordsPaginationOut,
)
def get_keywords(
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    personal_labels: Dict = Depends(deps.get_personal_labels),
    q: Optional[str] = Query(None, description="query keywords"),
    offset: int = Query(0),
    limit: Optional[int] = Query(None),
) -> Dict:
    """
    Get keywords and aliases
    """
    filter_f = partial(filter_keyword, q) if q else None
    items = list(labels_to_keywords(personal_labels, filter_f))
    if settings.REVERSE_KEYWORDS_OUTPUT:
        items.reverse()

    res = {"total": len(items), "items": paginate(items, offset, limit)}
    return {"result": res}


@router.post("/", response_model=KeywordsCreateOut)
def create_keywords(
    *,
    keywords_input: KeywordsCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    cache: CacheClient = Depends(deps.get_cache),
    personal_labels: Dict = Depends(deps.get_personal_labels),
) -> Any:
    """
    Batch create given keywords and aliases to keywords list
    """
    user_id = current_user.id
    new_labels = list(keywords_to_labels(keywords_input.keywords))
    logger.info("old labels: %s\nnew labels: %s", personal_labels, new_labels)

    dups = find_duplication_in_labels(personal_labels, new_labels)
    if dups:
        return {"result": {"failed": dups}}

    controller_client.add_labels(user_id, new_labels, keywords_input.dry_run)
    cache.delete_personal_keywords()
    return {"result": {"failed": []}}


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
    user_id = current_user.id
    updated_keyword = Keyword(name=keyword, aliases=aliases_in.aliases)
    logger.info("updated keyword: %s", updated_keyword)

    labels = list(keywords_to_labels([updated_keyword]))
    resp = controller_client.add_labels(user_id, labels, False)
    logger.info("[controller] response for update label: %s", resp)

    failed = []
    if resp.get("label_collection"):
        for failed_label in resp["label_collection"]["labels"]:
            failed += [failed_label["name"]] + failed_label["aliases"]

    if not failed:
        # clean cached key when changes happen
        cache.delete_personal_keywords()
    return {"result": {"failed": failed}}


def paginate(items: List[Any], offset: int = 0, limit: Optional[int] = None) -> List[Any]:
    """
    Mimic the behavior of database query's offset-limit pagination
    """
    end = limit + offset if limit is not None else None
    return items[offset:end]


def filter_keyword(query: str, keyword: Dict) -> bool:
    for matching_string in [keyword["name"], *keyword["aliases"]]:
        if query in matching_string:
            return True
    return False

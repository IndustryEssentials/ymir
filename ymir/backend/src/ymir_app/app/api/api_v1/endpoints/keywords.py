from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.logger import logger

from app import models
from app.api import deps
from app.config import settings
from app.schemas import (
    KeywordsCreate,
    KeywordsCreateOut,
    KeywordsPaginationOut,
    KeywordUpdate,
)
from app.utils.cache import CacheClient
from app.utils.ymir_controller import ControllerClient
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

    res = {"total": len(items), "items": paginate(items, offset, limit)}
    return {"result": res}


@router.post("/", response_model=KeywordsCreateOut)
def create_keywords(
    *,
    keywords_input: KeywordsCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    cache: CacheClient = Depends(deps.get_cache),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Batch create given keywords and aliases to keywords list
    """
    new_user_labels = UserLabels(labels=keywords_input.keywords)
    dups = user_labels.find_dups(new_user_labels)
    if dups:
        logger.info(f"find dups in new_user_labels {new_user_labels}")
        return {"result": {"failed": dups}}

    return process_update_labels(
        user_id=current_user.id,
        user_labels=user_labels,
        new_user_labels=new_user_labels,
        dry_run=keywords_input.dry_run,
        controller_client=controller_client,
        cache=cache,
    )


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
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    updated_label = SingleLabel(name=keyword, aliases=aliases_in.aliases)
    new_user_labels = UserLabels(labels=[updated_label])
    return process_update_labels(
        user_id=current_user.id,
        user_labels=user_labels,
        new_user_labels=new_user_labels,
        dry_run=False,
        controller_client=controller_client,
        cache=cache,
    )


def paginate(items: List[Any], offset: int = 0, limit: Optional[int] = None) -> List[Any]:
    """
    Mimic the behavior of database query's offset-limit pagination
    """
    end = limit + offset if limit is not None else None
    return items[offset:end]


def process_update_labels(
    user_id: int,
    user_labels: UserLabels,
    new_user_labels: UserLabels,
    dry_run: bool,
    controller_client: ControllerClient,
    cache: CacheClient,
) -> Dict:
    logger.info(f"old labels: {user_labels.json()}\nnew labels: {new_user_labels.json()}")
    resp = controller_client.add_labels(user_id, new_user_labels, dry_run)
    logger.info(f"[controller] response for update label: {resp}")

    conflict_labels = []
    if resp.get("label_collection"):
        for conflict_label in resp["label_collection"]["labels"]:
            conflict_labels += [conflict_label["name"]] + conflict_label["aliases"]

    if not conflict_labels:
        # clean cached key when changes happen
        cache.delete_personal_keywords_cache()
    return {"result": {"failed": conflict_labels}}

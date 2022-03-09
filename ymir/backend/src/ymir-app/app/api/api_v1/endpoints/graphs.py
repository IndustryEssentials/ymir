from enum import Enum
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.api.errors.errors import DatasetNotFound, GraphNotFound, ModelNotFound
from app.config import settings
from app.utils.graph import GraphClient

router = APIRouter()


class NodeType(str, Enum):
    dataset = "dataset"
    model = "model"


@router.get(
    "/",
    response_model=schemas.GraphOut,
    responses={404: {"description": "Node Not Found"}},
)
def get_graph(
    db: Session = Depends(deps.get_db),
    graph_db: GraphClient = Depends(deps.get_graph_client_of_user),
    type_: NodeType = Query(..., alias="type", description="type of Node, including model and dataset"),
    id_: int = Query(..., alias="id", description="model_id or dataset_id"),
    max_hops: int = Query(settings.MAX_HOPS, description="max distance from given node to target nodes"),
) -> Any:
    """
    Get history of dataset or model in Graph

    type: "model" or "dataset"
    id: model_id or dataset_id
    max_hops: max distence
    """
    node_obj = getattr(crud, type_).get(db, id=id_)
    if not node_obj:
        if type_ == "dataset":
            raise DatasetNotFound()
        else:
            raise ModelNotFound()

    source = {
        "label": type_.capitalize(),
        "hash": node_obj.hash,
        "id": id_,
    }
    # find all the nodes within max_hops pointing to the source
    # and all the nodes the source node pointing to (1 hop)
    res = graph_db.query_history(source, max_hops)
    if not res:
        raise GraphNotFound()

    return {"result": res}

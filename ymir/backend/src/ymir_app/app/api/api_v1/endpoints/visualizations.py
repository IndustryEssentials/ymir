from enum import Enum
from typing import Any

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import VisualizationNotFound, TaskNotFound
from app.utils.ymir_controller import ControllerClient


router = APIRouter()


class SortField(Enum):
    id = "id"
    create_datetime = "create_datetime"


@router.get("/", response_model=schemas.VisualizationPaginationOut)
def list_visualizations(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    name: str = Query(None),
    project_id: int = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
    order_by: SortField = Query(SortField.create_datetime),
    is_desc: bool = Query(True),
) -> Any:
    """
    Get visualization task list

    filter:
    - name

    order_by:
    - id
    - create_datetime
    """
    visualizations, total = crud.visualization.get_multi_visualizations(
        db,
        user_id=current_user.id,
        name=name,
        project_id=project_id,
        offset=offset,
        limit=limit,
        order_by=order_by.name,
        is_desc=is_desc,
    )
    return {"result": {"total": total, "items": visualizations}}


@router.post("/", response_model=schemas.VisualizationOut)
def create_visualization(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    obj_in: schemas.VisualizationCreate,
) -> Any:
    """
    Create visualization task
    """
    tasks = crud.task.get_multi_by_ids(db, ids=obj_in.task_ids)
    if not tasks:
        raise TaskNotFound()

    visualization = crud.visualization.create_visualization(db, user_id=current_user.id, conf_thr=obj_in.conf_thr,
                                                            iou_thr=obj_in.iou_thr, project_id=obj_in.project_id)

    for task in tasks:
        crud.task_visual_relationship.create_relationship(db, task_id=task.id, visualization_id=visualization.id)

    project_id = tasks[0].project_id
    datasets = [
        {"name": task.result_dataset.name, "hash": task.result_dataset.hash}  # type: ignore
        for task in tasks
    ]
    controller_client.create_visualization(current_user.id, project_id, visualization.tid, datasets)
    return {"result": visualization}


@router.delete(
    "/{visualization_id}",
    response_model=schemas.VisualizationOut,
)
def delete_visualization(
    *,
    db: Session = Depends(deps.get_db),
    visualization_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete visualization task
    (soft delete actually)
    """
    visualizations = crud.visualization.get(db, id=visualization_id)
    if not visualizations:
        raise VisualizationNotFound()

    visualization = crud.visualization.soft_remove(db, id=visualization_id)
    return {"result": visualization}

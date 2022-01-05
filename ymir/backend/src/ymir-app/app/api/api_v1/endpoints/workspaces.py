from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import DuplicateWorkspaceError, FailedtoCreateWorkspace
from app.utils.ymir_controller import (
    ControllerClient,
    ControllerRequest,
    ExtraRequestType,
)

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.WorkspaceOut,
    responses={400: {"description": "Username Already Exists"}},
)
def create_workspace(
    *,
    db: Session = Depends(deps.get_db),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    current_user: models.User = Depends(deps.get_current_active_user),
    name: str = Body(None),
    hash_: str = Body(None, alias="hash"),
) -> Any:
    """
    Create a workspace
    """
    # todo use dedicated func to generate all the hashes,
    #  including workspace_hash, task_hash, etc
    hash_ = hash_ or f"{current_user.id:0>6}"
    name = name or hash_
    workspace = crud.workspace.get_by_name(db, name=name)
    if workspace:
        raise DuplicateWorkspaceError()

    workspace_in = schemas.WorkspaceCreate(
        hash=hash_, name=name, user_id=current_user.id
    )

    workspace = crud.workspace.create(db, obj_in=workspace_in)

    req = ControllerRequest(ExtraRequestType.create_workspace, current_user.id, hash_)
    try:
        resp = controller_client.send(req)
    except ValueError:
        # todo parse error message
        raise FailedtoCreateWorkspace()

    return {"result": workspace}


@router.get("/mine", response_model=schemas.WorkspaceOut)
def get_my_workspace(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    current_workspace: models.Workspace = Depends(deps.get_current_workspace),
) -> Any:
    """
    Get workspace of current user
    """
    return {"result": current_workspace}

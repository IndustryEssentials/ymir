from typing import Any, Dict, Iterator

from fastapi import APIRouter, Depends, Path, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.api.errors.errors import (
    DockerImageHavingRelationships,
    DockerImageNotFound,
    DuplicateDockerImageError,
)
from app.constants.state import DockerImageType, ObjectType, ResultState
from app.schemas.image import DockerImageCreate
from app.libs.tasks import create_pull_docker_image_task

router = APIRouter()


@router.get("/", response_model=schemas.DockerImagesOut)
def list_docker_images(
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    name: str = Query(None),
    url: str = Query(None),
    state: ResultState = Query(None),
    type_: DockerImageType = Query(None, alias="type"),
    object_type: ObjectType = Query(None),
    is_official: bool = Query(None),
) -> Any:
    """
    Get docker images and configuration templates

    docker_image_type:
    1. training
    2. mining
    3. inference
    """
    docker_images, total = crud.docker_image.get_multi_with_filter(
        db,
        name=name,
        url=url,
        state=state,
        type=type_,
        object_type=object_type,
        is_official=is_official,
    )
    return {"result": {"total": total, "items": docker_images}}


@router.post("/", response_model=schemas.TaskOut)
def create_docker_image(
    *,
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_admin),
    docker_image_in: DockerImageCreate,
) -> Any:
    """
    Create docker image
    This endpint will create an image record immediately,
    but the pulling process will run in background
    """
    logger.info("[create image] received request to pull docker image: %s", docker_image_in.json())
    if crud.docker_image.get_by_url(db, docker_image_in.url) or crud.docker_image.get_by_name(db, docker_image_in.name):
        raise DuplicateDockerImageError()

    task_in_db = create_pull_docker_image_task(db, current_user.id, docker_image_in)
    return {"result": task_in_db}


def parse_docker_image_config(configs: Dict) -> Iterator[Dict]:
    for image_type, config in configs.items():
        if config:
            yield {
                "type": int(DockerImageType(int(image_type))),
                "config": config,
            }


@router.get(
    "/{docker_image_id}",
    response_model=schemas.DockerImageOut,
    responses={404: {"description": "Docker Image Not Found"}},
)
def get_docker_image(
    *,
    db: Session = Depends(deps.get_db),
    docker_image_id: int = Path(...),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a single docker image
    """
    docker_image = crud.docker_image.get(db, id=docker_image_id)
    if not docker_image:
        raise DockerImageNotFound()

    return {"result": docker_image}


@router.patch(
    "/{docker_image_id}",
    response_model=schemas.DockerImageOut,
    responses={404: {"description": "Docker Image Not Found"}},
)
def update_docker_image(
    *,
    db: Session = Depends(deps.get_db),
    docker_image_id: int = Path(...),
    docker_image_update: schemas.DockerImageUpdate,
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update docker image's name and description
    """
    docker_image = crud.docker_image.get(db, id=docker_image_id)
    if not docker_image:
        raise DockerImageNotFound()

    if docker_image_update.name and crud.docker_image.get_by_name(db, name=docker_image_update.name):
        raise DuplicateDockerImageError()

    docker_image = crud.docker_image.update(db, db_obj=docker_image, obj_in=docker_image_update)
    return {"result": docker_image}


@router.delete(
    "/{docker_image_id}",
    response_model=schemas.DockerImageOut,
)
def delete_docker_image(
    *,
    db: Session = Depends(deps.get_db),
    docker_image_id: int = Path(...),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete docker image
    (soft delete actually)
    """
    docker_image = crud.docker_image.get(db, id=docker_image_id)
    if not docker_image:
        raise DockerImageNotFound()

    having_relationships = crud.image_relationship.having_relationships(db, image_id=docker_image_id)
    if having_relationships:
        raise DockerImageHavingRelationships()

    docker_image = crud.docker_image.soft_remove(db, id=docker_image_id)
    return {"result": docker_image}


@router.put("/{docker_image_id}/related", response_model=schemas.ImageRelationshipsOut)
def link_docker_images(
    *,
    db: Session = Depends(deps.get_db),
    docker_image_id: int = Path(...),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_admin),
    image_relationships: schemas.ImageRelationshipsCreate,
) -> Any:
    """
    Make link docker images as user request
    for now, you can link a training image with multiple mining images
    """
    dest_image_ids = image_relationships.dest_image_ids
    existing_dest_images = crud.docker_image.get_multi_by_ids(db, ids=dest_image_ids)
    if len(existing_dest_images) != len(dest_image_ids):
        raise DockerImageNotFound()

    relationships = crud.image_relationship.make_relationships_as(
        db, src_image_id=docker_image_id, dest_image_ids=dest_image_ids
    )

    return {"result": relationships}


@router.get("/{docker_image_id}/related", response_model=schemas.ImageRelationshipsOut)
def get_related_images(
    *,
    db: Session = Depends(deps.get_db),
    docker_image_id: int = Path(...),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all the related_images of given docker image
    """
    relationships = crud.image_relationship.get_relationships_of_src_image(db, src_image_id=docker_image_id)
    return {"result": relationships}

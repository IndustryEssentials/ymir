from typing import Any, Dict, Iterator, List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
)
from fastapi.encoders import jsonable_encoder
from fastapi.logger import logger
from requests.exceptions import ConnectionError, HTTPError, Timeout
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DockerImageHavingRelationships,
    DockerImageNotFound,
    DuplicateDockerImageError,
    DuplicateWorkspaceError,
    FailedtoCreateWorkspace,
    FailedtoShareDockerImage,
)
from app.models.image import DockerImage
from app.schemas.image import (
    DockerImageCreate,
    DockerImageSharing,
    DockerImageState,
    DockerImageType,
    DockerImageUpdate,
    DockerImageUpdateConfig,
)
from app.utils.sheet import WufooAPI
from app.utils.ymir_controller import ControllerClient, ControllerRequest

router = APIRouter()


@router.get("/", response_model=schemas.DockerImagesOut)
def list_docker_images(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    name: str = Query(None),
    state: DockerImageState = Query(None),
    type_: DockerImageType = Query(None, alias="type"),
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
        state=state,
        type=type_,
    )
    return {"result": {"total": total, "items": docker_images}}


@router.post("/", response_model=schemas.DockerImageOut)
def create_docker_image(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_admin),
    docker_image_in: DockerImageCreate,
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Create docker image
    This endpint will create an image record immediately,
    but the pulling process will run in background
    """
    docker_image = crud.docker_image.create(db, obj_in=docker_image_in)
    logger.info("[create image] docker image record created: %s", docker_image)

    background_tasks.add_task(
        import_docker_image, db, controller_client, docker_image, current_user.id
    )
    return {"result": docker_image}


def import_docker_image(
    db: Session,
    controller_client: ControllerClient,
    docker_image: DockerImage,
    user_id: int,
) -> None:
    if not docker_image.url:
        logger.error("docker url not provided, skip")
        return

    try:
        resp = controller_client.pull_docker_image(docker_image.url, user_id)
    except ValueError:
        logger.exception("[create image] failed to import docker image via controller")
        state = DockerImageState.error
        crud.docker_image.update_state(db, docker_image=docker_image, state=state)
        return

    logger.info("[create image] docker image imported via controller: %s", resp)
    docker_image_dict = jsonable_encoder(docker_image)

    # note: we've created a placeholder record beforehand, update it first
    image_configs = parse_docker_image_config(resp)
    try:
        first_image_config = next(image_configs)
    except StopIteration:
        logger.error("[create image] failed to parse docker image via controller")
        crud.docker_image.update_state(
            db, docker_image=docker_image, state=DockerImageState.error
        )
        return

    docker_image_update = DockerImageUpdateConfig(
        **{**docker_image_dict, **first_image_config}
    )
    crud.docker_image.update(db, db_obj=docker_image, obj_in=docker_image_update)

    # if there are reminding configs, add new record
    for image in image_configs:
        docker_image_in = DockerImageCreate(**{**docker_image_dict, **image})
        docker_image = crud.docker_image.create(db, obj_in=docker_image_in)


def parse_docker_image_config(resp: Dict) -> Iterator[Dict]:
    configs = resp["docker_image_config"]
    hash_ = resp["hash_id"]
    for image_type, config in configs.items():
        if config:
            yield {
                "type": int(DockerImageType(int(image_type))),
                "state": int(DockerImageState.done),
                "hash": hash_,
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
    current_user: models.User = Depends(deps.get_current_active_user),
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
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update docker image's name and description
    """
    docker_image = crud.docker_image.get(db, id=docker_image_id)
    if not docker_image:
        raise DockerImageNotFound()

    docker_image = crud.docker_image.update(
        db, db_obj=docker_image, obj_in=docker_image_update
    )
    return {"result": docker_image}


@router.delete(
    "/{docker_image_id}",
    response_model=schemas.DockerImageOut,
)
def delete_docker_image(
    *,
    db: Session = Depends(deps.get_db),
    docker_image_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete docker image
    (soft delete actually)
    """
    docker_image = crud.docker_image.get(db, id=docker_image_id)
    if not docker_image:
        raise DockerImageNotFound()

    having_relationships = crud.image_relationship.having_relationships(
        db, image_id=docker_image_id
    )
    if having_relationships:
        raise DockerImageHavingRelationships()

    docker_image = crud.docker_image.soft_remove(db, id=docker_image_id)
    return {"result": docker_image}


@router.put("/{docker_image_id}/related", response_model=schemas.ImageRelationshipsOut)
def link_docker_images(
    *,
    db: Session = Depends(deps.get_db),
    docker_image_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_admin),
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
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all the related_images of given docker image
    """
    relationships = crud.image_relationship.get_relationships_of_src_image(
        db, src_image_id=docker_image_id
    )
    return {"result": relationships}


@router.post("/{docker_image_id}/share", response_model=schemas.DockerImageOut)
def share_image(
    *,
    db: Session = Depends(deps.get_db),
    docker_image_id: int = Path(...),
    shared_info: DockerImageSharing,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Request to share docker image to Ymir Team's Gallery
    """
    docker_image = crud.docker_image.get(db, id=docker_image_id)
    if not docker_image:
        raise DockerImageNotFound()
    payload = {"docker_name": docker_image.url, **shared_info.dict()}
    try:
        WufooAPI(payload).send()
    except (ConnectionError, HTTPError, Timeout):
        logger.exception("[share image] failed to share docker image")
        raise FailedtoShareDockerImage()

    # mark this image as shared
    docker_image = crud.docker_image.update_sharing_status(
        db=db, docker_image=docker_image, is_shared=True
    )
    return {"result": docker_image}

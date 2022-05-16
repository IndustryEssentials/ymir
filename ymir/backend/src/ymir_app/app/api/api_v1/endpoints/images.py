from typing import Any, Dict, Iterator, List

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query
from fastapi.logger import logger
from fastapi_cache.decorator import cache
from requests.exceptions import ConnectionError, HTTPError, Timeout
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DockerImageHavingRelationships,
    DockerImageNotFound,
    DuplicateDockerImageError,
    FailedtoGetSharedDockerImages,
    FailedtoShareDockerImage,
    InvalidSharedImageConfig,
)
from app.config import settings
from app.constants.state import DockerImageState, DockerImageType
from app.models.image import DockerImage
from app.schemas.image import (
    DockerImageCreate,
    DockerImageSharing,
    SharedDockerImageOut,
    SharedDockerImagesOut,
)
from app.utils.github import get_github_table
from app.utils.sheet import WufooAPI
from app.utils.ymir_controller import ControllerClient

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
    if crud.docker_image.docker_name_exists(db, url=docker_image_in.url):
        raise DuplicateDockerImageError()
    docker_image = crud.docker_image.create(db, obj_in=docker_image_in)
    logger.info("[create image] docker image record created: %s", docker_image)

    background_tasks.add_task(import_docker_image, db, controller_client, docker_image, current_user.id)
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
        crud.docker_image.update_state(db, docker_image=docker_image, state=DockerImageState.error)
        return

    # add new config in docker_image_config tbl
    hash_ = resp["hash_id"]
    image_configs = list(parse_docker_image_config(resp["docker_image_config"]))
    for image_config in image_configs:
        image_config_in = schemas.ImageConfigCreate(
            image_id=docker_image.id,
            **image_config,
        )
        crud.image_config.create(db, obj_in=image_config_in)

    crud.docker_image.update_from_dict(
        db,
        docker_image_id=docker_image.id,
        updates={"hash": hash_, "state": int(DockerImageState.done)},
    )
    logger.info(
        "[create image] docker image imported via controller: %s, added %d configs",
        resp,
        len(image_configs),
    )


def parse_docker_image_config(configs: Dict) -> Iterator[Dict]:
    for image_type, config in configs.items():
        if config:
            yield {
                "type": int(DockerImageType(int(image_type))),
                "config": config,
            }


@router.get("/shared", response_model=SharedDockerImagesOut)
async def get_shared_images(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get shared images from Ymir Team's Gallery (hosted on GitHub)
    """
    if not settings.SHARED_DOCKER_IMAGES_URL:
        raise InvalidSharedImageConfig()
    try:
        shared_images = await get_shared_images_from_github(
            settings.SHARED_DOCKER_IMAGES_URL, timeout=settings.GITHUB_TIMEOUT
        )
    except (ConnectionError, HTTPError, Timeout):
        logger.exception("[share image] failed get shared docker images")
        raise FailedtoGetSharedDockerImages()
    return {"result": shared_images}


@cache(expire=settings.APP_CACHE_EXPIRE_IN_SECONDS)
async def get_shared_images_from_github(url: str, timeout: int) -> List[Dict]:
    logger.info("[share image] getting shared docker images from GitHub...")
    shared_images = get_github_table(url, timeout=timeout)
    return shared_images


@router.post("/shared", response_model=SharedDockerImageOut)
def share_image(
    *,
    db: Session = Depends(deps.get_db),
    shared_image: DockerImageSharing,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Request to share docker image to Ymir Team's Gallery
    """
    docker_image = crud.docker_image.get(db, id=shared_image.docker_image_id)
    if not docker_image:
        raise DockerImageNotFound()

    functions = [DockerImageType(config.type).name for config in docker_image.configs]
    shared_info = {
        "docker_name": docker_image.url,
        "hash": docker_image.hash,
        "functions": ", ".join(functions),
        "description": docker_image.description,
        "contributor": shared_image.contributor,
        "phone": shared_image.phone,
        "email": shared_image.email,
        "organization": shared_image.organization,
    }
    try:
        WufooAPI().create_row(shared_info)
    except (ConnectionError, HTTPError, Timeout):
        logger.exception("[share image] failed to share docker image")
        raise FailedtoShareDockerImage()

    # mark this image as shared
    crud.docker_image.update_sharing_status(db=db, docker_image=docker_image, is_shared=True)
    return {"result": shared_image}


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
    current_user: models.User = Depends(deps.get_current_active_admin),
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
    relationships = crud.image_relationship.get_relationships_of_src_image(db, src_image_id=docker_image_id)
    return {"result": relationships}

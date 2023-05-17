import json
from typing import Dict

from sqlalchemy.orm import Session

from app import crud, schemas
from tests.utils.utils import random_lower_string


def create_docker_image_and_configs(db: Session, config: Dict = {}, image_type: int = 1):
    j = {"url": random_lower_string(), "name": random_lower_string()}

    docker_image_in = schemas.DockerImageCreate(**j)
    docker_image = crud.docker_image.create(db, obj_in=docker_image_in)
    crud.docker_image.update_state(db, docker_image=docker_image, state=schemas.DockerImageState.done)

    image_config_in = schemas.ImageConfigCreate(
        image_id=docker_image.id,
        config=json.dumps(config),
        type=image_type,
    )
    image_config = crud.image_config.create(db, obj_in=image_config_in)
    return docker_image, image_config

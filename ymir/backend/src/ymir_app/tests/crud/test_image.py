import json

from sqlalchemy.orm import Session

from app import crud, schemas
from app.constants.state import DockerImageState, DockerImageType
from app.schemas.image import DockerImageCreate
from tests.utils.utils import random_lower_string


class TestCreateImage:
    def test_create_image(self, db: Session) -> None:
        name = random_lower_string(10)
        url = random_lower_string()
        description = random_lower_string()
        obj_in = DockerImageCreate(db=db, name=name, url=url, description=description)
        image = crud.docker_image.create(db=db, obj_in=obj_in)
        assert image.name == name
        assert image.url == url


class TestListImages:
    def test_list_images(self, db: Session) -> None:
        images, count = crud.docker_image.get_multi_with_filter(db=db, state=DockerImageState.error)
        assert images == []
        assert count == 0

        image = crud.docker_image.get_multi(db=db, limit=1)[0]
        crud.docker_image.update_state(db=db, docker_image=image, state=DockerImageState.error)
        images, count = crud.docker_image.get_multi_with_filter(db=db, state=DockerImageState.error)
        crud.docker_image.update_state(db=db, docker_image=image, state=DockerImageState.done)
        assert images == [image]
        assert count == 1


class TestGetInferenceImages:
    def test_get_inference_images(self, db: Session) -> None:
        name = random_lower_string(10)
        url = random_lower_string()
        hash_ = random_lower_string(12)
        description = random_lower_string()
        obj_in = DockerImageCreate(
            db=db,
            name=name,
            hash=hash_,
            url=url,
            description=description,
            state=DockerImageState.done,
            config=json.dumps({}),
        )
        created_image = crud.docker_image.create(db=db, obj_in=obj_in)

        image_config_in = schemas.ImageConfigCreate(
            image_id=created_image.id,
            config=json.dumps({}),
            type=int(DockerImageType.infer),
        )
        crud.image_config.create(db, obj_in=image_config_in)

        fetched_image = crud.docker_image.get_inference_docker_image(db, url=url)
        assert fetched_image is not None
        assert created_image.hash == fetched_image.hash

from sqlalchemy.orm import Session

from app import crud
from app.schemas.image import DockerImageCreate
from tests.utils.utils import random_lower_string


def insert_image(db: Session):
    name = random_lower_string(10)
    url = random_lower_string()
    description = random_lower_string()
    obj_in = DockerImageCreate(db=db, name=name, url=url, description=description)
    image = crud.docker_image.create(db=db, obj_in=obj_in)
    return image


class TestImageHavingRelationships:
    def test_image_having_relationships(self, db: Session) -> None:
        image_1 = insert_image(db)
        image_2 = insert_image(db)
        crud.image_relationship.make_relationships_as(db, src_image_id=image_1.id, dest_image_ids=[image_2.id])
        assert crud.image_relationship.having_relationships(db, image_id=image_1.id)
        assert crud.image_relationship.having_relationships(db, image_id=image_2.id)

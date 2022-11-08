import time
import json

from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import settings
from app.constants.role import Roles
from app.db import base  # noqa: F401
from app.utils.security import frontend_hash
from app.utils.ymir_controller import ControllerClient


# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    roles = crud.role.get_multi(db)
    if not roles:
        for role in [Roles.NORMAL, Roles.ADMIN, Roles.SUPER_ADMIN]:
            role_in = schemas.RoleCreate(name=role.name, description=role.description)
            crud.role.create(db, obj_in=role_in)

    user = crud.user.get_by_email(db, email=settings.FIRST_ADMIN)
    if not user:
        password = frontend_hash(settings.FIRST_ADMIN_PASSWORD)
        user_in = schemas.UserCreate(
            email=settings.FIRST_ADMIN,
            password=password,
        )
        user = crud.user.create(db, obj_in=user_in)  # noqa: F841
        user = crud.user.activate(db, user=user)
        user = crud.user.update_role(db, user=user, role=schemas.UserRole.SUPER_ADMIN)

        if settings.INIT_LABEL_FOR_FIRST_USER:
            controller = ControllerClient(settings.GRPC_CHANNEL)
            controller.create_user(user_id=user.id)

    docker_images = crud.docker_image.get_multi(db)
    if not docker_images and settings.RUNTIMES:
        runtimes = json.loads(settings.RUNTIMES)
        for runtime in runtimes:
            docker_image = crud.docker_image.create(db, obj_in=schemas.DockerImageCreate(**runtime))  # noqa: F841
            crud.docker_image.update_state(db, docker_image=docker_image, state=schemas.DockerImageState.done)

            for config in runtime["configs"]:
                image_config_in = schemas.ImageConfigCreate(
                    image_id=docker_image.id,
                    config=json.dumps(config),
                    type=int(config["type"]),
                )
                crud.image_config.create(db, obj_in=image_config_in)


def migrate_data(db: Session) -> None:
    """
    migrate data from pre-1.3.0 version:
    1. create default model stage
    2. update dataset keywords structure (in {"gt": <content>, "pred": <content>} format)
    """
    total_models = crud.model.total(db)
    models = crud.model.get_multi(db, limit=total_models)
    for model in models:
        if model.recommended_stage:
            # no need to migrate
            continue
        if not model.map:
            # skip model without map
            continue
        if model.default_stage:
            stage = model.default_stage
        else:
            stage = crud.model_stage.create(
                db,
                obj_in=schemas.ModelStageCreate(
                    name="default_best_stage", map=model.map, timestamp=int(time.time()), model_id=model.id
                ),
            )
        crud.model.update_recommonded_stage(db, model_id=model.id, stage_id=stage.id)

    total_datasets = crud.dataset.total(db)
    datasets = crud.dataset.get_multi(db, limit=total_datasets)
    for dataset in datasets:
        crud.dataset.migrate_keywords(db, id=dataset.id)

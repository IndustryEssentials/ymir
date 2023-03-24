from typing import Any

from fastapi import APIRouter, Depends

from app import schemas
from app.api import deps
from app.api.errors.errors import (
    FailedToCreateUser,
)
from app.utils.ymir_controller import ControllerClient, gen_user_hash

router = APIRouter()


@router.post(
    "/controller",
    response_model=schemas.user.ControllerUserOut,
    dependencies=[Depends(deps.api_key_security)],
)
def create_controller_user(
    *,
    in_user: schemas.user.ControllerUserCreate,
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Register controller user
    """
    try:
        controller_client.create_user(user_id=in_user.user_id)
    except ValueError:
        raise FailedToCreateUser()

    return {"result": {"hash": gen_user_hash(in_user.user_id)}}

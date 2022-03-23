from typing import Any

import grpc
from fastapi import APIRouter, Depends

from app import models, schemas
from app.api import deps
from app.api.errors.errors import FailedtoGetSysInfo
from app.utils.ymir_controller import ControllerClient

router = APIRouter()


@router.get(
    "/",
    response_model=schemas.SysInfoOut,
)
def get_sys_info(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Get current system information, available GPUs for example
    """
    try:
        gpu_info = controller_client.get_gpu_info(current_user.id)
    except grpc.RpcError:
        raise FailedtoGetSysInfo()
    return {"result": gpu_info}

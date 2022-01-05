import random
import secrets
from typing import Any, List

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    UploadFile,
)
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    AssetNotFound,
    DatasetNotFound,
    DuplicateDatasetError,
    NoDatasetPermission,
    WorkspaceNotFound,
)
from app.config import settings
from app.utils.files import host_file, md5_of_file
from app.utils.ymir_controller import ControllerClient
from app.utils.ymir_viz import VizClient

router = APIRouter()


@router.post(
    "/uploadfile/",
    response_model=schemas.Msg,
)
def upload(
    *,
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload a file, return an url that has access to it
    """
    url = host_file(file)
    return {"result": url}

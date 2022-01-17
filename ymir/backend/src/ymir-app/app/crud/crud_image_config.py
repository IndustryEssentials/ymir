from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.config import settings
from app.constants.state import DockerImageState, DockerImageType
from app.crud.base import CRUDBase
from app.models.image_config import DockerImageConfig
from app.schemas.image_config import ImageConfigCreate, ImageConfigUpdate


class CRUDDockerImageConfig(
    CRUDBase[DockerImageConfig, ImageConfigCreate, ImageConfigUpdate]
):
    pass


image_config = CRUDDockerImageConfig(DockerImageConfig)

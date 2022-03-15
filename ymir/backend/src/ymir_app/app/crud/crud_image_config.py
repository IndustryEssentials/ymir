from app.crud.base import CRUDBase
from app.models.image_config import DockerImageConfig
from app.schemas.image_config import ImageConfigCreate, ImageConfigUpdate


class CRUDDockerImageConfig(CRUDBase[DockerImageConfig, ImageConfigCreate, ImageConfigUpdate]):
    pass


image_config = CRUDDockerImageConfig(DockerImageConfig)

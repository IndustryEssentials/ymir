from typing import Optional

from pydantic import BaseSettings


class VizSettings(BaseSettings):
    BACKEND_SANDBOX_ROOT: str = "/data/mir_root"

    VIZ_REDIS_URI: str = "redis://"

    # the middle data structure, it will save into cache,like Redis
    VIZ_MIDDLE_VERSION: str = "0.1"

    # redis key info
    VIZ_KEY_ASSET_DETAIL: str = "viz_key_detail"
    VIZ_KEY_ASSET_INDEX: str = "viz_key_index"
    # added all assets index by viz
    VIZ_ALL_INDEX_CLASSIDS: str = "__all_index_classids__"
    # set flag status when generating cache
    VIZ_CACHE_STATUS: str = "viz_key_status"

    VIZ_SENTRY_DSN: Optional[str] = None
    REDIS_TESTING: bool = False

    VIZ_DEBUG_MODE: bool = False


viz_settings = VizSettings(_env_file=".env")  # type: ignore

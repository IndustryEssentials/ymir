import os

env = os.environ.get

SANDBOX_ROOT: str = env("SANDBOX_ROOT", '/data/mir_root')

VIZ_REDIS_URI: str = env("VIZ_REDIS_URI", "redis://")

# redis key info
ASSET_ID_DETAIL = "viz_key_detail"
ASSETS_ATTRIBUTES = "viz_key_assets_attributes"
ASSETS_CLASS_ID_INDEX = "viz_key_index"

# the middle data structure, it will save into cache,like Redis
MIDDLE_STRUCTURE_VERSION = "0.1"

# added all assets index by viz
ALL_INDEX_CLASSIDS = "__all_index_classids__"
# set flag status when generating cache
CACHE_STATUS = "viz_key_status"

VIZ_SENTRY_DSN = env("VIZ_SENTRY_DSN", None)

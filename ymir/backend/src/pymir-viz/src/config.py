import os

env = os.environ.get

SANDBOX_ROOT = env("SANDBOX_ROOT", '/data/mir_root')

REDIS_URI = env("VIZ_REDIS_URI", "redis://")

# redis key info
ASSET_ID_DETAIL = "detail"
ASSETS_ATTRIBUTES = "assets_attributes"
ASSETS_CLASS_ID_INDEX = "index"

# the middle data structure, it will save into cache,like Redis
MIDDLE_STRUCTURE_VERSION = "0.1"

# added all assets index by viz
ALL_INDEX_CLASSIDS = "__all_index_classids__"
# set flag status when generating cache
CACHE_STATUS = "status"

VIZ_SENTRY_DSN = env("VIZ_SENTRY_DSN", None)

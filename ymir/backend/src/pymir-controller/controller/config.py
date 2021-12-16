import os

env = os.environ.get

# start labelling model env
LABEL_STUDIO = "label_studio"
# set your label tool
LABEL_TOOL = env("LABEL_TOOL", LABEL_STUDIO)
LABEL_STUDIO_TOKEN = env("LABEL_STUDIO_TOKEN", "Token ")
LABEL_STUDIO_HOST = env("LABEL_STUDIO_OPEN_HOST", "") + ":" + env("LABEL_STUDIO_OPEN_PORT", "")

REDIS_URI = env("REDIS_URI", "redis://:@127.0.0.1:6379")
# task_monitor_file
MONITOR_MAPPING_KEY = "monitor_mapping"
LABEL_TASK_LOOP_SECONDS = int(env("LABEL_TASK_LOOP_SECONDS", 5 * 60))

TASK_RUNNING = "running"
TASK_DONE = "done"
TASK_ERROR = "error"

# end labelling model env

# key of locking gpu
GPU_LOCKING_SET = "gpu_locking_set"

# labels.csv
RESERVE_COLUMN = 1

# get label studio tasks's slice number
LABEL_PAGE_SIZE = 500

# gpu usage for dispach
GPU_USAGE_THRESHOLD = float(env("GPU_USAGE_THRESHOLD", 0.8))
# gpu lock time
GPU_LOCK_MINUTES = int(env("GPU_LOCK_MINUTES", 1))

CONTROLLER_SENTRY_DSN = env("CONTROLLER_SENTRY_DSN", None)

IMAGE_TRAINING_CONFIG_PATH = "/img-man/training-template.yaml"
IMAGE_MINING_CONFIG_PATH = "/img-man/mining-template.yaml"
IMAGE_INFER_CONFIG_PATH = "/img-man/infer-template.yaml"

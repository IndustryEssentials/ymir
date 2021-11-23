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

import os

env = os.environ.get

# start labelling model env
LABEL_STUDIO = "label_studio"
LABEL_FREE = "label_free"
# set your label tool
LABEL_TOOL = env("LABEL_TOOL", LABEL_STUDIO)
if LABEL_TOOL == LABEL_STUDIO:
    LABEL_TOOL_HOST_URL = "http://labelstudio:8080"
    LABEL_TOOL_TOKEN = f"Token {env('LABEL_TOOL_TOKEN')}"
else:
    # LABEL_FREE
    LABEL_TOOL_HOST_URL = "http://label-nginx"
    LABEL_TOOL_TOKEN = f"Bearer {env('LABEL_TOOL_TOKEN')}"

# task_monitor_file
MONITOR_MAPPING_KEY = "monitor_mapping"
LABEL_TASK_LOOP_SECONDS = int(env("LABEL_TASK_LOOP_SECONDS", 5 * 60))
LABEL_TOOL_TIMEOUT = int(env("LABEL_TOOL_TIMEOUT", 600))
# end labelling model env

# get label studio tasks's slice number
LABEL_PAGE_SIZE = 500

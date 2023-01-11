import os

env = os.environ.get

# start labelling model env
LABEL_STUDIO = "label_studio"
LABEL_FREE = "label_free"
# set your label tool
LABEL_TOOL = env("LABEL_TOOL", LABEL_STUDIO)
# compatible with both "Token abc" and "abc" format
LABEL_TOOL_TOKEN = env("LABEL_TOOL_TOKEN").split()[-1]   # type: ignore
if LABEL_TOOL == LABEL_STUDIO:
    LABEL_TOOL_HOST_URL = "http://labelstudio:8080"
    LABEL_TOOL_TOKEN = f"Token {LABEL_TOOL_TOKEN}"
else:
    # LABEL_FREE
    LABEL_TOOL_HOST_URL = "http://label-nginx"
    LABEL_TOOL_TOKEN = f"Bearer {LABEL_TOOL_TOKEN}"

# task_monitor_file
MONITOR_MAPPING_KEY = "monitor_mapping"
LABEL_TASK_LOOP_SECONDS = int(env("LABEL_TASK_LOOP_SECONDS", 5 * 60))
LABEL_TOOL_TIMEOUT = int(env("LABEL_TOOL_TIMEOUT", 600))
# end labelling model env

# get label studio tasks's slice number
LABEL_PAGE_SIZE = 500

# MIR coco
MIR_COCO_ANNOTATION_FILENAME = "coco-annotations.json"

import os

env = os.environ.get

# LabelFree related
LABEL_TOOL = env("LABEL_TOOL")
LABEL_TOOL_HOST_URL = "http://label-nginx"
LABEL_TOOL_TOKEN = f"Bearer {env('LABEL_TOOL_TOKEN')}"

# task_monitor_file
MONITOR_MAPPING_KEY = "monitor_mapping"
LABEL_TASK_LOOP_SECONDS = int(env("LABEL_TASK_LOOP_SECONDS", 5 * 60))
LABEL_TOOL_TIMEOUT = int(env("LABEL_TOOL_TIMEOUT", 600))
# end labelling model env

# get label studio tasks's slice number
LABEL_PAGE_SIZE = 500

# MIR coco
MIR_COCO_ANNOTATION_FILENAME = "coco-annotations.json"

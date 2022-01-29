import os

env = os.environ.get

# start labelling model env
LABEL_STUDIO = "label_studio"
AIOS = "aios"
# set your label tool
LABEL_TOOL = env("LABEL_TOOL", LABEL_STUDIO)
LABEL_TOOL_URL = env("LABEL_TOOL_URL")
LABEL_TOOL_TOKEN = env("LABEL_TOOL_TOKEN")

# task_monitor_file
MONITOR_MAPPING_KEY = "monitor_mapping"
LABEL_TASK_LOOP_SECONDS = int(env("LABEL_TASK_LOOP_SECONDS", 5 * 60))
# end labelling model env

# labels.csv
LABEL_RESERVE_COLUMN = 1

# get label studio tasks's slice number
LABEL_PAGE_SIZE = 500

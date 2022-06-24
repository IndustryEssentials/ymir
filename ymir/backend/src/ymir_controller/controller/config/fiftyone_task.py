import os


FIFTYONE_URL = os.environ.get("FIFTYONE_URL", "http://127.0.0.1:5151/api/task")
FIFTYONE_TIMEOUT = int(os.environ.get("FIFTYONE_TIMEOUT", 60))

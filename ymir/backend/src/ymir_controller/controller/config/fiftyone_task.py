import os
env = os.environ.get


FIFTYONE_URL = env("FIFTYONE_URL", "http://127.0.0.1:5151/api/task")
FIFTYONE_TIMEOUT = int(env("FIFTYONE_TIMEOUT", 60))
FIFTYONE_CONCURRENT_LIMIT = int(env("FIFTYONE_CONCURRENT_LIMIT", 10))

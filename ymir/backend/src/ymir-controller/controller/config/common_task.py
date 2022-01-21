import os

from proto import backend_pb2

# redis service
BACKEND_REDIS_URL = os.environ.get("BACKEND_REDIS_URL", "redis://:@127.0.0.1:6379")

IMAGE_CONFIG_PATH = {
    backend_pb2.TaskType.TaskTypeTraining: "/img-man/training-template.yaml",
    backend_pb2.TaskType.TaskTypeMining: "/img-man/mining-template.yaml",
    backend_pb2.TaskType.TaskTypeInfer: "/img-man/infer-template.yaml",
}

MONITOR_URL = os.environ.get("MONITOR_URL", "http://127.0.0.1:9098")

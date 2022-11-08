import os

from mir.protos import mir_command_pb2 as mir_cmd_pb

# redis service
BACKEND_REDIS_URL = os.environ.get("BACKEND_REDIS_URL", "redis://:@127.0.0.1:6379")

IMAGE_CONFIG_PATH = {
    mir_cmd_pb.TaskType.TaskTypeTraining: "/img-man/training-template.yaml",
    mir_cmd_pb.TaskType.TaskTypeMining: "/img-man/mining-template.yaml",
    mir_cmd_pb.TaskType.TaskTypeInfer: "/img-man/infer-template.yaml",
}

IMAGE_LIVECODE_CONFIG_PATH = "/img-man/code-access.yaml"

MONITOR_URL = os.environ.get("MONITOR_URL", "http://127.0.0.1:9098")

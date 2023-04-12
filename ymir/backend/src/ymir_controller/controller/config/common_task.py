import os

from mir.protos import mir_command_pb2 as mir_cmd_pb

# redis service
BACKEND_REDIS_URL = os.environ.get("BACKEND_REDIS_URL", "redis://:@127.0.0.1:6379")

IMAGE_MANIFEST_PATH = "/img-man/manifest.yaml"
IMAGE_CONFIG_ROOT = "/img-man"
IMAGE_CONFIG_DIR_NAMES = {
    mir_cmd_pb.ModelObjectType.MOT_DET_BOX: "det",
    mir_cmd_pb.ModelObjectType.MOT_SEM_SEG: "semantic-seg",
    mir_cmd_pb.ModelObjectType.MOT_INS_SEG: "instance-seg",
}
IMAGE_CONFIG_FILE_NAMES = {
    mir_cmd_pb.TaskType.TaskTypeTraining: "training-template.yaml",
    mir_cmd_pb.TaskType.TaskTypeMining: "mining-template.yaml",
    mir_cmd_pb.TaskType.TaskTypeInfer: "infer-template.yaml",
}

MONITOR_URL = os.environ.get("MONITOR_URL", "http://127.0.0.1:9098")

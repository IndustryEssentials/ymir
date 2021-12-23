import os

from proto import backend_pb2

# redis service
CTR_REDIS_URI = os.environ.get("CTR_REDIS_URI", "redis://:@127.0.0.1:6379")


IMAGE_CONFIG_PATH = {
    backend_pb2.TaskType.TaskTypeTraining: "/img-man/training-template.yaml",
    backend_pb2.TaskType.TaskTypeMining: "/img-man/mining-template.yaml",
    backend_pb2.TaskType.TaskTypeInfer: "/img-man/infer-template.yaml",
}

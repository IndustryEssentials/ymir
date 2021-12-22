from enum import IntEnum

from proto import backend_pb2 as mirsvrpb


class DockerImageType(IntEnum):
    unknown = mirsvrpb.TaskType.TaskTypeUnknown
    training = mirsvrpb.TaskType.TaskTypeTraining
    mining = mirsvrpb.TaskType.TaskTypeMining
    infer = mirsvrpb.TaskType.TaskTypeInfer


class DockerImageState(IntEnum):
    pending = mirsvrpb.TaskState.TaskStatePending
    done = mirsvrpb.TaskState.TaskStateDone
    error = mirsvrpb.TaskState.TaskStateError

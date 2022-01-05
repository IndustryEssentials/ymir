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


class TaskType(IntEnum):
    unknown = mirsvrpb.TaskType.TaskTypeUnknown
    training = mirsvrpb.TaskType.TaskTypeTraining
    mining = mirsvrpb.TaskType.TaskTypeMining
    label = mirsvrpb.TaskType.TaskTypeLabel
    filter = mirsvrpb.TaskType.TaskTypeFilter
    import_data = mirsvrpb.TaskType.TaskTypeImportData
    export_data = mirsvrpb.TaskType.TaskTypeExportData
    copy_data = mirsvrpb.TaskType.TaskTypeCopyData
    merge = mirsvrpb.TaskType.TaskTypeMerge
    infer = mirsvrpb.TaskType.TaskTypeInfer


class TaskState(IntEnum):
    unknown = mirsvrpb.TaskState.TaskStateUnknown
    pending = mirsvrpb.TaskState.TaskStatePending
    running = mirsvrpb.TaskState.TaskStateRunning
    done = mirsvrpb.TaskState.TaskStateDone
    error = mirsvrpb.TaskState.TaskStateError
    terminate = 100
    premature = 101  # terminate task while try to get result prematurely

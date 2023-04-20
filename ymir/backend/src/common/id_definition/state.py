from enum import IntEnum

from mir.protos import mir_command_pb2 as mir_cmd_pb


class TaskType(IntEnum):
    training = mir_cmd_pb.TaskTypeTraining
    mining = mir_cmd_pb.TaskTypeMining
    label = mir_cmd_pb.TaskTypeLabel
    filter = mir_cmd_pb.TaskTypeFilter
    merge = mir_cmd_pb.TaskTypeMerge
    fusion = mir_cmd_pb.TaskTypeFusion
    infer = mir_cmd_pb.TaskTypeDatasetInfer


class TaskState(IntEnum):
    unknown = mir_cmd_pb.TaskStateUnknown
    pending = mir_cmd_pb.TaskStatePending
    running = mir_cmd_pb.TaskStateRunning
    done = mir_cmd_pb.TaskStateDone
    error = mir_cmd_pb.TaskStateError
    terminate = mir_cmd_pb.TaskStateTerminate


class ResultType(IntEnum):
    no_result = 0
    dataset = 1
    model = 2
    prediction = 3
    docker_image = 4


class ResultState(IntEnum):
    processing = 0
    ready = 1
    error = 2


class ObjectType(IntEnum):
    unknown = mir_cmd_pb.OT_UNKNOWN
    classification = mir_cmd_pb.OT_CLASS
    object_detect = mir_cmd_pb.OT_DET_BOX
    segmentation = mir_cmd_pb.OT_SEG
    instance_segmentation = 4


class AnnotationType(IntEnum):
    gt = 1
    pred = 2


class DockerImageType(IntEnum):
    unknown = 0
    training = 1
    mining = 2
    infer = 9


class DockerImageState(IntEnum):
    pending = 1
    done = 3
    error = 4


class ImportStrategy(IntEnum):
    no_annotations = 1
    ignore_unknown_annotations = 2
    stop_upon_unknown_annotations = 3
    add_unknown_annotations = 4

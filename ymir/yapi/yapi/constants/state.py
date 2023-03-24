from enum import IntEnum


class TaskState(IntEnum):
    unknown = 0
    pending = 1
    running = 2
    done = 3
    error = 4
    terminate = 100


class ResultType(IntEnum):
    no_result = 0
    dataset = 1
    model = 2
    prediction = 3


class ResultState(IntEnum):
    processing = 0
    ready = 1
    error = 2


class ObjectType(IntEnum):
    unknown = 0
    classification = 1
    object_detect = 2
    segmentation = 3
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


RunningStates = [TaskState.pending, TaskState.running]
FinalStates = [TaskState.done, TaskState.error, TaskState.terminate]

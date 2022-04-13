from enum import IntEnum

from common_utils.percent_log_util import LogState
from proto import backend_pb2 as mirsvrpb


class DockerImageType(IntEnum):
    unknown = mirsvrpb.TaskType.TaskTypeUnknown
    training = mirsvrpb.TaskType.TaskTypeTraining
    mining = mirsvrpb.TaskType.TaskTypeMining
    infer = mirsvrpb.TaskType.TaskTypeInfer


class DockerImageState(IntEnum):
    pending = LogState.PENDING
    done = LogState.DONE
    error = LogState.PENDING.ERROR


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
    data_fusion = mirsvrpb.TaskType.TaskTypeFusion
    copy_model = mirsvrpb.TaskType.TaskTypeCopyModel
    import_model = mirsvrpb.TaskType.TaskTypeImportModel
    dataset_infer = mirsvrpb.TaskType.TaskTypeDatasetInfer

    # fixme
    #  create_project is not the type of TASK_CREATE, but empty dataset need a task
    create_project = mirsvrpb.RequestType.REPO_CREATE


class TaskState(IntEnum):
    unknown = LogState.UNKNOWN
    pending = LogState.PENDING
    running = LogState.RUNNING
    done = LogState.DONE
    error = LogState.ERROR
    terminate = 100


class ResultType(IntEnum):
    no_result = 0
    dataset = 1
    model = 2


class ResultState(IntEnum):
    processing = 0
    ready = 1
    error = 2


class IterationStage(IntEnum):
    prepare_mining = 0
    mining = 1
    label = 2
    prepare_training = 3
    training = 4
    end = 5


class MiningStrategy(IntEnum):
    chunk = 0
    dedup = 1
    customize = 2


class TrainingType(IntEnum):
    object_detect = 1


RunningStates = [TaskState.pending, TaskState.running]
FinalStates = [TaskState.done, TaskState.error, TaskState.terminate]

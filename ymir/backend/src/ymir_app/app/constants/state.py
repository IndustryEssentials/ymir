from dataclasses import dataclass
from enum import IntEnum

from common_utils.percent_log_util import LogState
from mir.protos import mir_command_pb2 as mir_cmd_pb
from proto import backend_pb2 as mirsvrpb


class DockerImageType(IntEnum):
    unknown = mir_cmd_pb.TaskType.TaskTypeUnknown
    training = mir_cmd_pb.TaskType.TaskTypeTraining
    mining = mir_cmd_pb.TaskType.TaskTypeMining
    infer = mir_cmd_pb.TaskType.TaskTypeInfer


class DockerImageState(IntEnum):
    pending = LogState.PENDING
    done = LogState.DONE
    error = LogState.PENDING.ERROR


class TaskType(IntEnum):
    unknown = mir_cmd_pb.TaskType.TaskTypeUnknown
    training = mir_cmd_pb.TaskType.TaskTypeTraining
    mining = mir_cmd_pb.TaskType.TaskTypeMining
    label = mir_cmd_pb.TaskType.TaskTypeLabel
    filter = mir_cmd_pb.TaskType.TaskTypeFilter
    import_data = mir_cmd_pb.TaskType.TaskTypeImportData
    export_data = mir_cmd_pb.TaskType.TaskTypeExportData
    copy_data = mir_cmd_pb.TaskType.TaskTypeCopyData
    merge = mir_cmd_pb.TaskType.TaskTypeMerge
    infer = mir_cmd_pb.TaskType.TaskTypeInfer
    data_fusion = mir_cmd_pb.TaskType.TaskTypeFusion
    copy_model = mir_cmd_pb.TaskType.TaskTypeCopyModel
    import_model = mir_cmd_pb.TaskType.TaskTypeImportModel
    dataset_infer = mir_cmd_pb.TaskType.TaskTypeDatasetInfer

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


class ObjectType(IntEnum):
    unknown = mir_cmd_pb.ObjectType.OT_UNKNOWN  # 0
    classification = mir_cmd_pb.ObjectType.OT_CLASS  # 1
    object_detect = mir_cmd_pb.ObjectType.OT_DET_BOX  # 2
    segmentation = mir_cmd_pb.ObjectType.OT_SEG  # 3
    instance_segmentation = mir_cmd_pb.ObjectType.OT_SEG + 1  # 4


class AnnotationType(IntEnum):
    gt = 1
    pred = 2


class DatasetType(IntEnum):
    validation = mir_cmd_pb.TvtTypeValidation
    training = mir_cmd_pb.TvtTypeTraining


@dataclass(frozen=True)
class IterationStepTemplate:
    name: str
    task_type: TaskType


RunningStates = [TaskState.pending, TaskState.running]
FinalStates = [TaskState.done, TaskState.error, TaskState.terminate]
IterationStepTemplates = [
    IterationStepTemplate("prepare_mining", TaskType.data_fusion),
    IterationStepTemplate("mining", TaskType.mining),
    IterationStepTemplate("label", TaskType.label),
    IterationStepTemplate("prepare_training", TaskType.data_fusion),
    IterationStepTemplate("training", TaskType.training),
]

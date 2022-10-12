from typing import Any

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.invoker.invoker_task_copy import TaskCopyInvoker
from controller.invoker.invoker_task_exporting import TaskExportingInvoker
from controller.invoker.invoker_task_fusion import TaskFusionInvoker
from controller.invoker.invoker_task_import_dataset import TaskImportDatasetInvoker
from controller.invoker.invoker_task_import_model import TaskImportModelInvoker
from controller.invoker.invoker_task_labeling import TaskLabelingInvoker
from controller.invoker.invoker_task_mining import TaskMiningInvoker
from controller.invoker.invoker_task_training import TaskTrainingInvoker
from mir.protos import mir_command_pb2 as mir_cmd_pb
from proto import backend_pb2


class CreateTaskInvokerFactory(BaseMirControllerInvoker):
    _create_task_invokers_map = {
        mir_cmd_pb.TaskType.TaskTypeCopyData: TaskCopyInvoker,
        mir_cmd_pb.TaskType.TaskTypeExportData: TaskExportingInvoker,
        mir_cmd_pb.TaskType.TaskTypeImportData: TaskImportDatasetInvoker,
        mir_cmd_pb.TaskType.TaskTypeMining: TaskMiningInvoker,
        mir_cmd_pb.TaskType.TaskTypeTraining: TaskTrainingInvoker,
        mir_cmd_pb.TaskType.TaskTypeLabel: TaskLabelingInvoker,
        mir_cmd_pb.TaskType.TaskTypeFusion: TaskFusionInvoker,
        mir_cmd_pb.TaskType.TaskTypeImportModel: TaskImportModelInvoker,
        mir_cmd_pb.TaskType.TaskTypeCopyModel: TaskCopyInvoker,
        mir_cmd_pb.TaskType.TaskTypeDatasetInfer: TaskMiningInvoker,
    }

    def __new__(cls, request: backend_pb2.GeneralReq, *args, **kwargs) -> Any:  # type: ignore
        sub_invoker_class = CreateTaskInvokerFactory._create_task_invokers_map[request.req_create_task.task_type]
        return sub_invoker_class(request=request, *args, **kwargs)  # type: ignore

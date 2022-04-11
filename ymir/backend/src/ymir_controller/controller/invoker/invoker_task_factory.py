from typing import Any

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.invoker.invoker_task_copy import TaskCopyInvoker
from controller.invoker.invoker_task_exporting import TaskExportingInvoker
from controller.invoker.invoker_task_filter import TaskFilterInvoker
from controller.invoker.invoker_task_fusion import TaskFusionInvoker
from controller.invoker.invoker_task_importing import TaskImportingInvoker
from controller.invoker.invoker_task_labeling import TaskLabelingInvoker
from controller.invoker.invoker_task_mining import TaskMiningInvoker
from controller.invoker.invoker_task_model_importing import TaskModelImportingInvoker
from controller.invoker.invoker_task_training import TaskTrainingInvoker
from proto import backend_pb2


class CreateTaskInvokerFactory(BaseMirControllerInvoker):
    _create_task_invokers_map = {
        backend_pb2.TaskTypeCopyData: TaskCopyInvoker,
        backend_pb2.TaskTypeExportData: TaskExportingInvoker,
        backend_pb2.TaskTypeFilter: TaskFilterInvoker,
        backend_pb2.TaskTypeImportData: TaskImportingInvoker,
        backend_pb2.TaskTypeMining: TaskMiningInvoker,
        backend_pb2.TaskTypeTraining: TaskTrainingInvoker,
        backend_pb2.TaskTypeLabel: TaskLabelingInvoker,
        backend_pb2.TaskTypeFusion: TaskFusionInvoker,
        backend_pb2.TaskTypeImportModel: TaskModelImportingInvoker,
        backend_pb2.TaskTypeCopyModel: TaskCopyInvoker,
        backend_pb2.TaskTypeDatasetInfer: TaskMiningInvoker,
    }

    def __new__(cls, request: backend_pb2.GeneralReq, *args, **kwargs) -> Any:  # type: ignore
        sub_invoker_class = CreateTaskInvokerFactory._create_task_invokers_map[request.req_create_task.task_type]
        return sub_invoker_class(request=request, *args, **kwargs)  # type: ignore

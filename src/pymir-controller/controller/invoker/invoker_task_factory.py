from typing import Any

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.invoker.invoker_task_copy import TaskCopyInvoker
from controller.invoker.invoker_task_exporting import TaskExportingInvoker
from controller.invoker.invoker_task_filter import TaskFilterInvoker
from controller.invoker.invoker_task_importing import TaskImportingInvoker
from controller.invoker.invoker_task_mining import TaskMiningInvoker
from controller.invoker.invoker_task_training import TaskTrainingInvoker
from controller.invoker.invoker_task_labeling import TaskLabelingInvoker
from ymir.protos import mir_common_pb2 as mir_common
from ymir.protos import mir_controller_service_pb2 as mirsvrpb


class CreateTaskInvokerFactory(BaseMirControllerInvoker):
    _create_task_invokers_map = {
        mir_common.TaskTypeCopyData: TaskCopyInvoker,
        mir_common.TaskTypeExportData: TaskExportingInvoker,
        mir_common.TaskTypeFilter: TaskFilterInvoker,
        mir_common.TaskTypeImportData: TaskImportingInvoker,
        mir_common.TaskTypeMining: TaskMiningInvoker,
        mir_common.TaskTypeTraining: TaskTrainingInvoker,
        mir_common.TaskTypeLabel: TaskLabelingInvoker
    }

    def __new__(cls, request: mirsvrpb.GeneralReq, *args, **kwargs) -> Any:  # type: ignore
        sub_invoker_class = CreateTaskInvokerFactory._create_task_invokers_map[request.req_create_task.task_type]
        return sub_invoker_class(request=request, *args, **kwargs)  # type: ignore

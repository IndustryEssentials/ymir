from controller.invoker import (
    invoker_task_factory,
    invoker_cmd_branch_list,
    invoker_cmd_branch_checkout,
    invoker_cmd_branch_commit,
    invoker_cmd_branch_create,
    invoker_cmd_branch_delete,
    invoker_cmd_filter,
    invoker_cmd_inference,
    invoker_cmd_init,
    invoker_cmd_log,
    invoker_cmd_merge,
    invoker_cmd_task_info,
    invoker_cmd_label_get,
    invoker_cmd_label_add,
)

from proto import backend_pb2

RequestTypeToInvoker = {
    backend_pb2.CMD_BRANCH_DEL: invoker_cmd_branch_delete.BranchDeleteInvoker,
    backend_pb2.CMD_BRANCH_LIST: invoker_cmd_branch_list.BranchListInvoker,
    backend_pb2.CMD_BRANCH_CHECKOUT: invoker_cmd_branch_checkout.BranchCheckoutInvoker,
    backend_pb2.CMD_BRANCH_CREATE: invoker_cmd_branch_create.BranchCreateInvoker,
    backend_pb2.CMD_COMMIT: invoker_cmd_branch_commit.BranchCommitInvoker,
    backend_pb2.CMD_FILTER: invoker_cmd_filter.FilterBranchInvoker,
    backend_pb2.CMD_INFERENCE: invoker_cmd_inference.InferenceCMDInvoker,
    backend_pb2.CMD_INIT: invoker_cmd_init.InitInvoker,
    backend_pb2.CMD_LOG: invoker_cmd_log.LogInvoker,
    backend_pb2.CMD_MERGE: invoker_cmd_merge.MergeInvoker,
    backend_pb2.REPO_CREATE: invoker_cmd_init.InitInvoker,
    backend_pb2.TASK_CREATE: invoker_task_factory.CreateTaskInvokerFactory,
    backend_pb2.TASK_INFO: invoker_cmd_task_info.GetTaskInfoInvoker,
    backend_pb2.CMD_LABEL_ADD: invoker_cmd_label_add.LabelAddInvoker,
    backend_pb2.CMD_LABEL_GET: invoker_cmd_label_get.LabelGetInvoker,
}

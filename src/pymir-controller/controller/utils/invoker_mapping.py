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
)

import ymir.protos.mir_controller_service_pb2 as mirsvrpb

RequestTypeToInvoker = {
    mirsvrpb.CMD_BRANCH_DEL: invoker_cmd_branch_delete.BranchDeleteInvoker,
    mirsvrpb.CMD_BRANCH_LIST: invoker_cmd_branch_list.BranchListInvoker,
    mirsvrpb.CMD_BRANCH_CHECKOUT: invoker_cmd_branch_checkout.BranchCheckoutInvoker,
    mirsvrpb.CMD_BRANCH_CREATE: invoker_cmd_branch_create.BranchCreateInvoker,
    mirsvrpb.CMD_COMMIT: invoker_cmd_branch_commit.BranchCommitInvoker,
    mirsvrpb.CMD_FILTER: invoker_cmd_filter.FilterBranchInvoker,
    mirsvrpb.CMD_INFERENCE: invoker_cmd_inference.InferenceCMDInvoker,
    mirsvrpb.CMD_INIT: invoker_cmd_init.InitInvoker,
    mirsvrpb.CMD_LOG: invoker_cmd_log.LogInvoker,
    mirsvrpb.CMD_MERGE: invoker_cmd_merge.MergeInvoker,
    mirsvrpb.REPO_CREATE: invoker_cmd_init.InitInvoker,
    mirsvrpb.TASK_CREATE: invoker_task_factory.CreateTaskInvokerFactory,
    mirsvrpb.TASK_INFO: invoker_cmd_task_info.GetTaskInfoInvoker,
}

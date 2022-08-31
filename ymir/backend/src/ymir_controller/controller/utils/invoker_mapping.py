from controller.invoker import (
    invoker_cmd_branch_commit,
    invoker_cmd_filter,
    invoker_cmd_gpu_info,
    invoker_cmd_inference,
    invoker_cmd_init,
    invoker_cmd_label_add,
    invoker_cmd_label_get,
    invoker_cmd_merge,
    invoker_cmd_pull_image,
    invoker_cmd_repo_check,
    invoker_cmd_repo_clear,
    invoker_cmd_sampling,
    invoker_cmd_terminate,
    invoker_cmd_user_create,
    invoker_task_factory,
)

from proto import backend_pb2

RequestTypeToInvoker = {
    backend_pb2.CMD_COMMIT: invoker_cmd_branch_commit.BranchCommitInvoker,
    backend_pb2.CMD_FILTER: invoker_cmd_filter.FilterBranchInvoker,
    backend_pb2.CMD_GPU_INFO_GET: invoker_cmd_gpu_info.GPUInfoInvoker,
    backend_pb2.CMD_INFERENCE: invoker_cmd_inference.InferenceCMDInvoker,
    backend_pb2.CMD_INIT: invoker_cmd_init.InitInvoker,
    backend_pb2.CMD_LABEL_ADD: invoker_cmd_label_add.LabelAddInvoker,
    backend_pb2.CMD_LABEL_GET: invoker_cmd_label_get.LabelGetInvoker,
    backend_pb2.CMD_MERGE: invoker_cmd_merge.MergeInvoker,
    backend_pb2.CMD_PULL_IMAGE: invoker_cmd_pull_image.ImageHandler,
    backend_pb2.CMD_TERMINATE: invoker_cmd_terminate.CMDTerminateInvoker,
    backend_pb2.CMD_REPO_CHECK: invoker_cmd_repo_check.RepoCheckInvoker,
    backend_pb2.CMD_REPO_CLEAR: invoker_cmd_repo_clear.RepoClearInvoker,
    backend_pb2.REPO_CREATE: invoker_cmd_init.InitInvoker,
    backend_pb2.TASK_CREATE: invoker_task_factory.CreateTaskInvokerFactory,
    backend_pb2.USER_CREATE: invoker_cmd_user_create.UserCreateInvoker,
    backend_pb2.CMD_SAMPLING: invoker_cmd_sampling.SamplingInvoker,
}

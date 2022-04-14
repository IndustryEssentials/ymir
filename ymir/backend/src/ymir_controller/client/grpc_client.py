import argparse
import logging
import sys
from typing import Any, Dict, Optional

import grpc
from google.protobuf import json_format

from controller.utils import invoker_call, revs
from proto import backend_pb2
from proto import backend_pb2_grpc


class ControllerClient:
    def __init__(self, channel: str, repo: str, user: str) -> None:
        channel = grpc.insecure_channel(channel)
        self.stub = backend_pb2_grpc.mir_controller_serviceStub(channel)
        self.user = user
        self.repo = repo
        self.executor_config = ''
        self.executor_name = ''

    def process_req(self, req: Any) -> Any:
        resp = self.stub.data_manage_request(req)
        if resp.code != 0:
            raise ValueError(f"gRPC error. response: {resp.code} {resp.message}")
        logging.info(json_format.MessageToDict(resp, preserving_proto_field_name=True, use_integers_for_enums=True))
        return resp


def _build_cmd_create_user_req(args: Dict) -> backend_pb2.GeneralReq:
    return invoker_call.make_cmd_request(user_id=args["user"], task_id=args["tid"], req_type=backend_pb2.USER_CREATE)


def _build_cmd_create_repo_req(args: Dict) -> backend_pb2.GeneralReq:
    return invoker_call.make_cmd_request(user_id=args["user"],
                                         repo_id=args["repo"],
                                         task_id=args["tid"],
                                         req_type=backend_pb2.REPO_CREATE)


def _build_cmd_add_labels_req(args: Dict) -> backend_pb2.GeneralReq:
    label_list = args["labels"].split(';')

    label = backend_pb2.Label()
    label.id = -1
    label.name = label_list[0]
    label.aliases.extend(label_list[1:])

    label_collection = backend_pb2.LabelCollection()
    label_collection.labels.append(label)
    return invoker_call.make_cmd_request(user_id=args["user"],
                                         repo_id=args["repo"],
                                         task_id=args["tid"],
                                         label_collection=label_collection,
                                         req_type=backend_pb2.CMD_LABEL_ADD)


def _build_cmd_get_labels_req(args: Dict) -> backend_pb2.GeneralReq:
    return invoker_call.make_cmd_request(user_id=args["user"],
                                         repo_id=args["repo"],
                                         task_id=args["tid"],
                                         req_type=backend_pb2.CMD_LABEL_GET)


def _build_cmd_sampling_req(args: Dict) -> backend_pb2.GeneralReq:
    return invoker_call.make_cmd_request(user_id=args["user"],
                                         repo_id=args["repo"],
                                         task_id=args["tid"],
                                         in_dataset_ids=args['in_dataset_ids'],
                                         sampling_count=args['sampling_count'],
                                         sampling_rate=args['sampling_rate'],
                                         req_type=backend_pb2.CMD_SAMPLING)


def call_cmd(client: ControllerClient, *, args: Any) -> Optional[str]:
    args = vars(args)
    req_name = "_build_cmd_{}_req".format(args['task_type'])
    req_func = getattr(sys.modules[__name__], req_name)
    req = req_func(args)
    return client.process_req(req)


def _build_task_filter_req(args: Dict) -> backend_pb2.GeneralReq:
    filter_request = backend_pb2.TaskReqFilter()
    filter_request.in_dataset_ids[:] = args['in_dataset_ids']
    if args.get('in_class_ids', None):
        filter_request.in_class_ids[:] = args['in_class_ids']
    if args.get('ex_class_ids', None):
        filter_request.ex_class_ids[:] = args['ex_class_ids']

    req_create_task = backend_pb2.ReqCreateTask()
    req_create_task.task_type = backend_pb2.TaskTypeFilter
    req_create_task.filter.CopyFrom(filter_request)

    return req_create_task


def _build_task_training_req(args: Dict) -> backend_pb2.GeneralReq:
    train_task_req = backend_pb2.TaskReqTraining()
    for in_dataset_id in args['in_dataset_ids']:
        train_task_req.in_dataset_types.append(revs.build_tvt_dataset_id(in_dataset_id))
    train_task_req.in_class_ids[:] = args['in_class_ids']

    req_create_task = backend_pb2.ReqCreateTask()
    req_create_task.task_type = backend_pb2.TaskTypeTraining
    req_create_task.no_task_monitor = args['no_task_monitor']
    req_create_task.training.CopyFrom(train_task_req)

    return req_create_task


def _build_task_mining_req(args: Dict) -> backend_pb2.GeneralReq:
    mine_task_req = backend_pb2.TaskReqMining()
    if args.get('top_k', None):
        mine_task_req.top_k = args['top_k']
    mine_task_req.in_dataset_ids[:] = args['in_dataset_ids']
    if args.get('ex_dataset_ids', None):
        mine_task_req.ex_dataset_ids[:] = args['ex_dataset_ids']

    req_create_task = backend_pb2.ReqCreateTask()
    req_create_task.task_type = backend_pb2.TaskTypeMining
    req_create_task.mining.CopyFrom(mine_task_req)

    return req_create_task


def _build_task_importing_req(args: Dict) -> backend_pb2.GeneralReq:
    importing_request = backend_pb2.TaskReqImporting()
    importing_request.asset_dir = args['asset_dir']
    importing_request.annotation_dir = args['annotation_dir']
    importing_request.name_strategy_ignore = args['name_strategy_ignore']

    req_create_task = backend_pb2.ReqCreateTask()
    req_create_task.task_type = backend_pb2.TaskTypeImportData
    req_create_task.no_task_monitor = args['no_task_monitor']
    req_create_task.importing.CopyFrom(importing_request)

    return req_create_task


def _build_task_labeling_req(args: Dict) -> backend_pb2.GeneralReq:
    labeling_request = backend_pb2.TaskReqLabeling()
    labeling_request.dataset_id = args['in_dataset_ids'][0]
    labeling_request.labeler_accounts[:] = args['labeler_accounts']
    labeling_request.in_class_ids[:] = args['in_class_ids']
    labeling_request.expert_instruction_url = args['expert_instruction_url']
    labeling_request.project_name = args['project_name']
    if args['keep_annotation']:
        labeling_request.export_annotation = True

    req_create_task = backend_pb2.ReqCreateTask()
    req_create_task.task_type = backend_pb2.TaskTypeLabel
    req_create_task.no_task_monitor = args['no_task_monitor']
    req_create_task.labeling.CopyFrom(labeling_request)

    return req_create_task


def _build_task_fusion_req(args: Dict) -> backend_pb2.GeneralReq:
    fusion_request = backend_pb2.TaskReqFusion()
    fusion_request.merge_strategy = backend_pb2.MergeStrategy.HOST
    fusion_request.in_dataset_ids[:] = args['in_dataset_ids']
    if args.get('ex_dataset_ids', None):
        fusion_request.ex_dataset_ids[:] = args['ex_dataset_ids']
    if args.get('in_class_ids', None):
        fusion_request.in_class_ids[:] = args['in_class_ids']
    if args.get('ex_class_ids', None):
        fusion_request.ex_class_ids[:] = args['ex_class_ids']
    if args.get('sampling_count', 0):
        fusion_request.count = args['sampling_count']
    elif args.get('sampling_rate', 0.0):
        fusion_request.rate = args['sampling_rate']

    req_create_task = backend_pb2.ReqCreateTask()
    req_create_task.task_type = backend_pb2.TaskTypeFusion
    req_create_task.no_task_monitor = args['no_task_monitor']
    req_create_task.fusion.CopyFrom(fusion_request)

    return req_create_task


def _build_task_import_model_req(args: Dict) -> backend_pb2.GeneralReq:
    req_create_task = backend_pb2.ReqCreateTask()
    req_create_task.task_type = backend_pb2.TaskTypeImportModel
    req_create_task.no_task_monitor = args['no_task_monitor']
    req_create_task.model_importing.model_package_path = args['model_package_path']

    return req_create_task


def _get_executor_config(args: Any) -> str:
    executor_config = ''
    if args['executor_config']:
        with open(args['executor_config'], 'r') as f:
            executor_config = f.read()
    return executor_config


def call_create_task(client: ControllerClient, *, args: Any) -> Optional[str]:
    args = vars(args)
    req_name = "_build_task_{}_req".format(args["task_type"])
    req_func = getattr(sys.modules[__name__], req_name)
    task_req = req_func(args)
    req = invoker_call.make_cmd_request(user_id=args["user"],
                                        repo_id=args["repo"],
                                        task_id=args["tid"],
                                        model_hash=args["model_hash"],
                                        req_type=backend_pb2.TASK_CREATE,
                                        req_create_task=task_req,
                                        executant_name=args['tid'],
                                        merge_strategy=1,
                                        docker_image_config=_get_executor_config(args),
                                        singleton_op=args['executor_name'],
                                        task_parameters=args['task_parameters'])
    logging.info(json_format.MessageToDict(req, preserving_proto_field_name=True, use_integers_for_enums=True))
    return client.process_req(req)


# TODO (phoenix): check and fix this.
# def call_check_task_status(client: ControllerClient, *, args: Any) -> List:
#     args = vars(args)
#     task_info_req = backend_pb2.ReqGetTaskInfo()
#     task_info_req.task_ids[:] = args["task_ids"]
#     req = invoker_call.make_cmd_request(user_id=args["user"],
#                                         repo_id=args["repo"],
#                                         task_id=args["tid"],
#                                         req_type=backend_pb2.TASK_INFO,
#                                         task_info_req=task_info_req)
#     return client.process_req(req)


def get_parser() -> Any:
    parser = argparse.ArgumentParser(description="controler caller")
    sub_parsers = parser.add_subparsers()

    common_group = parser.add_argument_group("common", "common parameters")
    common_group.add_argument(
        "-g",
        "--grpc",
        default="127.0.0.1:50066",
        type=str,
        help="grpc channel",
    )
    common_group.add_argument("-u", "--user", type=str, help="default user")
    common_group.add_argument("-r", "--repo", type=str, help="default mir repo")
    common_group.add_argument("-t", "--tid", type=str, help="task id")
    common_group.add_argument("--model_hash", type=str, help="model hash")
    common_group.add_argument("--labels", type=str, help="labels to be added, seperated by comma.")

    # CMD CALL
    parser_cmd_call = sub_parsers.add_parser("cmd_call", help="create sync cmd call")
    parser_cmd_call.add_argument("--task_type",
                                 choices=["create_user", "create_repo", "add_labels", "get_labels", "sampling"],
                                 type=str,
                                 help="task type")
    parser_cmd_call.add_argument("--in_dataset_ids", nargs="*", type=str)
    sampling_group = parser_cmd_call.add_mutually_exclusive_group()
    sampling_group.add_argument("--sampling_count", type=int, help="sampling count")
    sampling_group.add_argument("--sampling_rate", type=float, help="sampling rate")
    parser_cmd_call.set_defaults(func=call_cmd)

    # CREATE TASK
    parser_create_task = sub_parsers.add_parser("create_task", help="create a long-running task")
    parser_create_task.add_argument(
        "--task_type",
        choices=["filter", "merge", "training", "mining", "importing", "labeling", "fusion", "import_model"],
        type=str,
        help="task type")
    parser_create_task.add_argument("--in_class_ids", nargs="*", type=int)
    parser_create_task.add_argument("--ex_class_ids", nargs="*", type=int)
    parser_create_task.add_argument("--in_dataset_ids", nargs="*", type=str)
    parser_create_task.add_argument("--ex_dataset_ids", nargs="*", type=str)
    parser_create_task.add_argument("--asset_dir", type=str)
    parser_create_task.add_argument("--annotation_dir", type=str)
    parser_create_task.add_argument("--name_strategy_ignore", action="store_true")
    parser_create_task.add_argument("--model_package_path", type=str)
    parser_create_task.add_argument("--top_k", type=int)
    parser_create_task.add_argument("--expert_instruction_url", type=str)
    parser_create_task.add_argument("--labeler_accounts", nargs="*", type=str)
    parser_create_task.add_argument("--project_name", type=str)
    parser_create_task.add_argument("--executor_config", type=str, default='')
    parser_create_task.add_argument("--executor_name", type=str, default='')
    parser_create_task.add_argument("--keep_annotation", action="store_true")
    parser_create_task.add_argument("--no_task_monitor", action="store_true")
    sampling_group = parser_create_task.add_mutually_exclusive_group()
    sampling_group.add_argument("--sampling_count", type=int, help="sampling count")
    sampling_group.add_argument("--sampling_rate", type=float, help="sampling rate")
    parser_create_task.add_argument("--task_parameters", type=str, default='')
    parser_create_task.set_defaults(func=call_create_task)

    return parser


def run() -> None:
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s] %(filename)s:%(lineno)s:%(funcName)s(): %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.DEBUG)
    logging.debug("in debug mode")

    parser = get_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        print("invalid argument, try -h to get more info")
        return

    logging.info(f"args: {args}")
    client = ControllerClient(args.grpc, args.repo, args.user)
    args.func(client, args=args)


if __name__ == "__main__":
    run()

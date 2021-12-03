import argparse
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import grpc
from google.protobuf import json_format

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controller.utils import invoker_call, revs
from proto import backend_pb2
from proto import backend_pb2_grpc


class ControllerClient:
    def __init__(self, channel: str, repo: str, user: str) -> None:
        channel = grpc.insecure_channel(channel)
        self.stub = backend_pb2_grpc.mir_controller_serviceStub(channel)
        self.user = user
        self.repo = repo

    def process_req(self, req: Any) -> Any:
        resp = self.stub.data_manage_request(req)
        if resp.code != 0:
            raise ValueError(f"gRPC error. response: {resp.code} {resp.message}")
        logging.info(json_format.MessageToDict(resp, preserving_proto_field_name=True, use_integers_for_enums=True))
        return resp


def _build_cmd_create_repo_req(args: Dict) -> backend_pb2.GeneralReq:
    return invoker_call.make_cmd_request(user_id=args["user"],
                                         repo_id=args["repo"],
                                         task_id=args["tid"],
                                         req_type=backend_pb2.REPO_CREATE)


def _build_cmd_add_labels_req(args: Dict) -> backend_pb2.GeneralReq:
    return invoker_call.make_cmd_request(user_id=args["user"],
                                         repo_id=args["repo"],
                                         task_id=args["tid"],
                                         req_type=backend_pb2.CMD_LABEL_ADD)

def _build_cmd_get_labels_req(args: Dict) -> backend_pb2.GeneralReq:
    return invoker_call.make_cmd_request(user_id=args["user"],
                                         repo_id=args["repo"],
                                         task_id=args["tid"],
                                         req_type=backend_pb2.CMD_LABEL_GET)


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
    req_create_task.no_task_monitor = True
    req_create_task.training.CopyFrom(train_task_req)

    return req_create_task


def _build_task_mining_req(args: Dict) -> backend_pb2.GeneralReq:
    mine_task_req = backend_pb2.TaskReqMining()
    if args.get('top_k', None):
        mine_task_req.top_k = args['top_k']
    mine_task_req.model_hash = args['model_hash']
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

    req_create_task = backend_pb2.ReqCreateTask()
    req_create_task.task_type = backend_pb2.TaskTypeImportData
    req_create_task.no_task_monitor = False
    req_create_task.importing.CopyFrom(importing_request)

    return req_create_task


def _build_task_labeling_req(args: Dict) -> backend_pb2.GeneralReq:
    labeling_request = backend_pb2.TaskReqLabeling()
    labeling_request.dataset_id = args['in_dataset_ids'][0]
    labeling_request.labeler_accounts[:] = args['labeler_accounts']
    labeling_request.in_class_ids[:] = args['in_class_ids']
    labeling_request.expert_instruction_url = args['expert_instruction_url']
    labeling_request.project_name = args['project_name']

    req_create_task = backend_pb2.ReqCreateTask()
    req_create_task.task_type = backend_pb2.TaskTypeLabel
    req_create_task.no_task_monitor = False
    req_create_task.labeling.CopyFrom(labeling_request)

    return req_create_task


def call_create_task(client: ControllerClient, *, args: Any) -> Optional[str]:
    args = vars(args)
    req_name = "_build_task_{}_req".format(args["task_type"])
    req_func = getattr(sys.modules[__name__], req_name)
    task_req = req_func(args)
    req = invoker_call.make_cmd_request(user_id=args["user"],
                                        repo_id=args["repo"],
                                        task_id=args["tid"],
                                        req_type=backend_pb2.TASK_CREATE,
                                        req_create_task=task_req)
    logging.info(json_format.MessageToDict(req, preserving_proto_field_name=True, use_integers_for_enums=True))
    return client.process_req(req)


def call_check_task_status(client: ControllerClient, *, args: Any) -> List:
    args = vars(args)
    task_info_req = backend_pb2.ReqGetTaskInfo()
    task_info_req.task_ids[:] = args["task_ids"]
    req = invoker_call.make_cmd_request(user_id=args["user"],
                                        repo_id=args["repo"],
                                        task_id=args["tid"],
                                        req_type=backend_pb2.TASK_INFO,
                                        task_info_req=task_info_req)
    return client.process_req(req)


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

    # CMD CALL
    parser_create_task = sub_parsers.add_parser("cmd_call", help="create sync cmd call")
    parser_create_task.add_argument("--task_type", choices=["create_repo", "add_labels", "get_labels"], type=str, help="task type")
    parser_create_task.set_defaults(func=call_cmd)

    # CREATE TASK
    parser_create_task = sub_parsers.add_parser("create_task", help="create a long-running task")
    parser_create_task.add_argument("--task_type",
                                    choices=["filter", "merge", "training", "mining", "importing", "labeling"],
                                    type=str,
                                    help="task type")
    parser_create_task.add_argument("--in_class_ids", nargs="*", type=int)
    parser_create_task.add_argument("--ex_class_ids", nargs="*", type=int)
    parser_create_task.add_argument("--in_dataset_ids", nargs="*", type=str)
    parser_create_task.add_argument("--ex_dataset_ids", nargs="*", type=str)
    parser_create_task.add_argument("--model_hash", type=str, help="model_hash")
    parser_create_task.add_argument("--asset_dir", type=str)
    parser_create_task.add_argument("--annotation_dir", type=str)
    parser_create_task.add_argument("--top_k", type=int)
    parser_create_task.add_argument("--expert_instruction_url", type=str)
    parser_create_task.add_argument("--labeler_accounts", nargs="*", type=str)
    parser_create_task.add_argument("--project_name", type=str)
    parser_create_task.set_defaults(func=call_create_task)

    # GET TASK INFO
    parser_get_task_info = sub_parsers.add_parser("get_task_info", help="checkout the status of given tasks")
    parser_get_task_info.add_argument("--task_ids", nargs="+", help="task ids")
    parser_get_task_info.set_defaults(func=call_check_task_status)

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

    client = ControllerClient(args.grpc, args.repo, args.user)
    args.func(client, args=args)


if __name__ == "__main__":
    run()

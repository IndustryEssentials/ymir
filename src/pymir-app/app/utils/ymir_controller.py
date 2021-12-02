import enum
import itertools
import secrets
import time
from dataclasses import dataclass
from typing import Dict, Generator, List, Union, Optional

import grpc
from google.protobuf import json_format  # type: ignore
from proto import backend_pb2 as mirsvrpb
from proto import backend_pb2_grpc as mir_grpc
from fastapi.logger import logger

from app.models.task import TaskType, Task
from app.schemas.dataset import ImportStrategy
from app.schemas.task import MergeStrategy
from id_definition.task_id import TaskId
from app.utils.files import purge_contents_of_a_dir


class ExtraRequestType(enum.IntEnum):
    create_workspace = 100
    get_task_info = 200
    inference = 300
    add_label = 400
    get_label = 401
    kill = 500


MERGE_STRATEGY_MAPPING = {
    MergeStrategy.stop_upon_conflict: mirsvrpb.STOP,
    MergeStrategy.prefer_newest: mirsvrpb.HOST,
    MergeStrategy.prefer_oldest: mirsvrpb.HOST,
}


def gen_typed_datasets(dataset_type: int, datasets: List[str]) -> Generator:
    for dataset_id in datasets:
        dataset_with_type = mirsvrpb.TaskReqTraining.TrainingDatasetType()
        dataset_with_type.dataset_type = dataset_type
        dataset_with_type.dataset_id = dataset_id
        yield dataset_with_type


@dataclass
class ControllerRequest:
    type: Union[TaskType, ExtraRequestType]
    user_id: Union[str, int]
    repo_id: Optional[str] = None
    task_id: Optional[str] = None
    args: Optional[Dict] = None
    req: Optional[mirsvrpb.GeneralReq] = None

    def __post_init__(self) -> None:
        if isinstance(self.user_id, int):
            self.user_id = f"{self.user_id:0>4}"
        if self.repo_id is None:
            self.repo_id = f"{self.user_id:0>6}"
        if self.task_id is None:
            self.task_id = self.gen_task_id(self.user_id)

        request = mirsvrpb.GeneralReq(
            user_id=self.user_id,
            repo_id=self.repo_id,
            task_id=self.task_id,
            executor_instance=self.task_id,
        )

        method_name = "prepare_" + self.type.name
        self.req = getattr(self, method_name)(request, self.args)

    @staticmethod
    def gen_task_id(user_id: Union[int, str]) -> str:
        user_id = f"{user_id:0>4}"
        repo_id = f"{user_id:0>6}"
        hex_task_id = f"{secrets.token_hex(3)}{int(time.time())}"
        return str(TaskId("t", "0", "00", user_id, repo_id, hex_task_id))

    def prepare_create_workspace(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.REPO_CREATE
        return request

    def prepare_get_task_info(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        req_get_task_info = mirsvrpb.ReqGetTaskInfo()
        req_get_task_info.task_ids[:] = args["task_ids"]

        request.req_type = mirsvrpb.TASK_INFO
        request.req_get_task_info.CopyFrom(req_get_task_info)
        return request

    def prepare_filter(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        filter_request = mirsvrpb.TaskReqFilter()
        filter_request.in_dataset_ids[:] = args["include_datasets"]
        if args.get("include_classes"):
            filter_request.in_class_ids[:] = args["include_classes"]
        if args.get("exclude_classes"):
            filter_request.ex_class_ids[:] = args["exclude_classes"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mirsvrpb.TaskTypeFilter
        req_create_task.filter.CopyFrom(filter_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.merge_strategy = MERGE_STRATEGY_MAPPING[args["strategy"]]
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_training(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        train_task_req = mirsvrpb.TaskReqTraining()

        datasets = itertools.chain(
            gen_typed_datasets(
                mirsvrpb.TvtTypeTraining, args.get("include_train_datasets", [])
            ),
            gen_typed_datasets(
                mirsvrpb.TvtTypeValidation, args.get("include_validation_datasets", []),
            ),
            gen_typed_datasets(
                mirsvrpb.TvtTypeTest, args.get("include_test_datasets", [])
            ),
        )
        for dataset in datasets:
            train_task_req.in_dataset_types.append(dataset)
        train_task_req.in_class_ids[:] = args["include_classes"]
        if "config" in args:
            train_task_req.training_config = args["config"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mirsvrpb.TaskTypeTraining
        req_create_task.no_task_monitor = False
        req_create_task.training.CopyFrom(train_task_req)

        request.req_type = mirsvrpb.TASK_CREATE
        request.merge_strategy = MERGE_STRATEGY_MAPPING[args["strategy"]]
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_mining(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        mine_task_req = mirsvrpb.TaskReqMining()
        if args.get("top_k", None):
            mine_task_req.top_k = args["top_k"]
        mine_task_req.model_hash = args["model_hash"]
        mine_task_req.in_dataset_ids[:] = args["include_datasets"]
        mine_task_req.generate_annotations = args["generate_annotations"]
        if "config" in args:
            mine_task_req.mining_config = args["config"]
        if args.get("exclude_datasets", None):
            mine_task_req.ex_dataset_ids[:] = args["exclude_datasets"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mirsvrpb.TaskTypeMining
        req_create_task.no_task_monitor = False
        req_create_task.mining.CopyFrom(mine_task_req)

        request.req_type = mirsvrpb.TASK_CREATE
        request.merge_strategy = MERGE_STRATEGY_MAPPING[args["strategy"]]
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_import_data(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        importing_request = mirsvrpb.TaskReqImporting()
        importing_request.asset_dir = args["asset_dir"]
        importing_request.annotation_dir = args["annotation_dir"]
        strategy = args.get("strategy") or ImportStrategy.ignore_unknown_annotations
        if strategy is ImportStrategy.ignore_unknown_annotations:
            importing_request.name_strategy_ignore = True
        elif strategy is ImportStrategy.stop_upon_unknown_annotations:
            importing_request.name_strategy_ignore = False
        elif strategy is ImportStrategy.no_annotations:
            # underlying stuff requires the `annotation_dir` anyway
            purge_contents_of_a_dir(args["annotation_dir"])
            # name_strategy_ignore has no effect actually, but it's required
            importing_request.name_strategy_ignore = False
        else:
            raise ValueError("not supported strategy: %s" % strategy.name)

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mirsvrpb.TaskTypeImportData
        req_create_task.no_task_monitor = False
        req_create_task.importing.CopyFrom(importing_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_label(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        label_request = mirsvrpb.TaskReqLabeling()
        label_request.project_name = args["name"]
        label_request.dataset_id = args["include_datasets"][0]
        label_request.labeler_accounts[:] = args["labellers"]
        label_request.in_class_ids[:] = args["include_classes"]
        if args.get("extra_url"):
            label_request.expert_instruction_url = args["extra_url"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mirsvrpb.TaskTypeLabel
        req_create_task.labeling.CopyFrom(label_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_copy_data(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        copy_request = mirsvrpb.TaskReqCopyData()
        strategy = args.get("strategy") or ImportStrategy.ignore_unknown_annotations
        if strategy is ImportStrategy.ignore_unknown_annotations:
            copy_request.name_strategy_ignore = True
        elif strategy is ImportStrategy.stop_upon_unknown_annotations:
            copy_request.name_strategy_ignore = False
        else:
            raise ValueError("not supported strategy: %s" % strategy.name)

        copy_request.src_user_id = args["src_user_id"]
        copy_request.src_repo_id = args["src_repo_id"]
        copy_request.src_dataset_id = args["src_dataset_id"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mirsvrpb.TaskTypeCopyData
        req_create_task.copy.CopyFrom(copy_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_inference(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_INFERENCE
        request.model_hash = args["model_hash"]
        request.asset_dir = args["asset_dir"]
        request.model_config = args["config"]
        return request

    def prepare_add_label(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        request.check_only = args["dry_run"]
        request.req_type = mirsvrpb.CMD_LABEL_ADD
        request.private_labels[:] = args["labels"]
        return request

    def prepare_get_label(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_LABEL_GET
        return request

    def prepare_kill(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        if args["is_label_task"]:
            request.req_type = mirsvrpb.CMD_LABLE_TASK_TERMINATE
        else:
            request.req_type = mirsvrpb.CMD_KILL
        request.executor_instance = args["target_container"]
        return request


class ControllerClient:
    def __init__(self, channel: str) -> None:
        self.channel = grpc.insecure_channel(channel)
        self.stub = mir_grpc.mir_controller_serviceStub(self.channel)

    def close(self) -> None:
        self.channel.close()

    def send(self, req: mirsvrpb.GeneralReq) -> Dict:
        resp = self.stub.data_manage_request(req.req)
        if resp.code != 0:
            raise ValueError(f"gRPC error. response: {resp.code} {resp.message}")
        return json_format.MessageToDict(
            resp,
            preserving_proto_field_name=True,
            use_integers_for_enums=True,
            including_default_value_fields=True,
        )

    def get_labels_of_user(self, user_id: int) -> List[str]:
        req = ControllerRequest(ExtraRequestType.get_label, user_id)
        resp = self.send(req)
        logger.info("[controller] get labels response: %s", resp)
        return list(resp["csv_labels"])

    def create_task(
        self,
        user_id: int,
        workspace_id: Optional[str],
        task_id: str,
        task_type: TaskType,
        task_parameters: Optional[Dict],
    ) -> Dict:
        req = ControllerRequest(task_type, user_id, workspace_id, task_id, args=task_parameters)
        return self.send(req)

    def terminate_task(self, user_id: int, target_task: Task) -> Dict:
        req = ControllerRequest(
            ExtraRequestType.kill,
            user_id=user_id,
            args={
                "target_container": target_task.hash,
                "is_label_task": target_task.type is TaskType.label,
            },
        )
        return self.send(req)

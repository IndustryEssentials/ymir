import enum
import itertools
import secrets
import time
from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional, Union

import grpc
from fastapi.logger import logger
from google.protobuf import json_format  # type: ignore

from app.constants.state import TaskType
from app.schemas.dataset import ImportStrategy, MergeStrategy
from id_definition.task_id import TaskId
from proto import backend_pb2 as mirsvrpb
from proto import backend_pb2_grpc as mir_grpc


class ExtraRequestType(enum.IntEnum):
    create_project = 100
    get_task_info = 200
    inference = 300
    add_label = 400
    get_label = 401
    kill = 500
    pull_image = 600
    get_gpu_info = 601
    create_user = 602


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


def gen_user_hash(user_id: int) -> str:
    return f"{user_id:0>4}"


def gen_repo_hash(project_id: int) -> str:
    return f"{project_id:0>6}"


def gen_task_hash(user_id: int, project_id: int) -> str:
    user_hash = gen_user_hash(user_id)
    repo_hash = gen_repo_hash(project_id)
    hex_task_id = f"{secrets.token_hex(3)}{int(time.time())}"
    return str(TaskId("t", "0", "00", user_hash, repo_hash, hex_task_id))


@dataclass
class ControllerRequest:
    type: Union[TaskType, ExtraRequestType]
    user_id: int
    project_id: int = 0
    task_id: Optional[str] = None
    args: Optional[Dict] = None
    req: Optional[mirsvrpb.GeneralReq] = None

    def __post_init__(self) -> None:
        user_hash = gen_user_hash(self.user_id)
        repo_hash = gen_repo_hash(self.project_id)
        task_hash = self.task_id or gen_task_hash(self.user_id, self.project_id)

        request = mirsvrpb.GeneralReq(
            user_id=user_hash,
            repo_id=repo_hash,
            task_id=task_hash,
        )

        method_name = "prepare_" + self.type.name
        self.req = getattr(self, method_name)(request, self.args)

    def prepare_create_user(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.USER_CREATE
        return request

    def prepare_create_project(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        # project training target labels
        request.in_class_ids[:] = args["training_classes"]
        request.req_type = mirsvrpb.REPO_CREATE
        return request

    def prepare_filter(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
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

    def prepare_training(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        train_task_req = mirsvrpb.TaskReqTraining()

        datasets = itertools.chain(
            gen_typed_datasets(mirsvrpb.TvtTypeTraining, args.get("include_train_datasets", [])),
            gen_typed_datasets(
                mirsvrpb.TvtTypeValidation,
                args.get("include_validation_datasets", []),
            ),
            gen_typed_datasets(mirsvrpb.TvtTypeTest, args.get("include_test_datasets", [])),
        )
        for dataset in datasets:
            train_task_req.in_dataset_types.append(dataset)
        train_task_req.in_class_ids[:] = args["include_classes"]
        if "model_hash" in args:
            request.model_hash = args["model_hash"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mirsvrpb.TaskTypeTraining
        req_create_task.no_task_monitor = False
        req_create_task.training.CopyFrom(train_task_req)

        request.req_type = mirsvrpb.TASK_CREATE
        request.singleton_op = args["docker_image"]
        request.docker_image_config = args["docker_config"]
        request.merge_strategy = MERGE_STRATEGY_MAPPING[args["strategy"]]
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_mining(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        mine_task_req = mirsvrpb.TaskReqMining()
        if args.get("top_k", None):
            mine_task_req.top_k = args["top_k"]
        mine_task_req.in_dataset_ids[:] = args["include_datasets"]
        mine_task_req.generate_annotations = args["generate_annotations"]
        if "exclude_datasets" in args:
            mine_task_req.ex_dataset_ids[:] = args["exclude_datasets"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mirsvrpb.TaskTypeMining
        req_create_task.no_task_monitor = False
        req_create_task.mining.CopyFrom(mine_task_req)

        request.req_type = mirsvrpb.TASK_CREATE
        request.merge_strategy = MERGE_STRATEGY_MAPPING[args["strategy"]]
        request.singleton_op = args["docker_image"]
        request.docker_image_config = args["docker_config"]
        request.model_hash = args["model_hash"]
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_import_data(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        importing_request = mirsvrpb.TaskReqImporting()
        importing_request.asset_dir = args["asset_dir"]
        strategy = args.get("strategy") or ImportStrategy.ignore_unknown_annotations
        if strategy != ImportStrategy.no_annotations:
            importing_request.annotation_dir = args["annotation_dir"]
        if strategy == ImportStrategy.ignore_unknown_annotations:
            importing_request.name_strategy_ignore = True
        else:
            importing_request.name_strategy_ignore = False

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mirsvrpb.TaskTypeImportData
        req_create_task.no_task_monitor = False
        req_create_task.importing.CopyFrom(importing_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_label(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        label_request = mirsvrpb.TaskReqLabeling()
        label_request.project_name = args["name"]
        label_request.dataset_id = args["include_datasets"][0]
        label_request.labeler_accounts[:] = args["labellers"]
        label_request.in_class_ids[:] = args["include_classes"]
        label_request.export_annotation = args["keep_annotations"]
        if args.get("extra_url"):
            label_request.expert_instruction_url = args["extra_url"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mirsvrpb.TaskTypeLabel
        req_create_task.labeling.CopyFrom(label_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_copy_data(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
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
        copy_request.src_dataset_id = args["src_resource_id"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mirsvrpb.TaskTypeCopyData
        req_create_task.copy.CopyFrom(copy_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_inference(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_INFERENCE
        request.model_hash = args["model_hash"]
        request.asset_dir = args["asset_dir"]
        request.singleton_op = args["docker_image"]
        request.docker_image_config = args["docker_config"]
        return request

    def prepare_add_label(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.check_only = args["dry_run"]
        request.req_type = mirsvrpb.CMD_LABEL_ADD
        request.private_labels[:] = args["labels"]
        return request

    def prepare_get_label(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_LABEL_GET
        return request

    def prepare_kill(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_TERMINATE
        request.executor_instance = args["target_container"]
        request.terminated_task_type = args["task_type"]
        return request

    def prepare_pull_image(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_PULL_IMAGE
        request.singleton_op = args["url"]
        return request

    def prepare_get_gpu_info(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_GPU_INFO_GET
        return request

    def prepare_data_fusion(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        data_fusion_request = mirsvrpb.TaskReqFusion()
        data_fusion_request.in_dataset_ids[:] = args["include_datasets"]
        data_fusion_request.merge_strategy = MERGE_STRATEGY_MAPPING[args["include_strategy"]]
        if args.get("exclude_datasets"):
            data_fusion_request.ex_dataset_ids[:] = args["exclude_datasets"]

        if args.get("include_class_ids"):
            data_fusion_request.in_class_ids[:] = args["include_class_ids"]
        if args.get("exclude_class_ids"):
            data_fusion_request.ex_class_ids[:] = args["exclude_class_ids"]

        if args.get("sampling_count"):
            data_fusion_request.count = args["sampling_count"]
        else:
            # not sampling
            data_fusion_request.rate = 1

        req_create_task = mirsvrpb.ReqCreateTask()

        req_create_task.task_type = mirsvrpb.TaskTypeFusion
        req_create_task.no_task_monitor = False
        req_create_task.fusion.CopyFrom(data_fusion_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request


class ControllerClient:
    def __init__(self, channel: str) -> None:
        self.channel = grpc.insecure_channel(channel)
        self.stub = mir_grpc.mir_controller_serviceStub(self.channel)

    def close(self) -> None:
        self.channel.close()

    def send(self, req: mirsvrpb.GeneralReq) -> Dict:
        logger.info("[controller] request: %s", req.req)
        resp = self.stub.data_manage_request(req.req)
        if resp.code != 0:
            raise ValueError(f"gRPC error. response: {resp.code} {resp.message}")
        logger.info("[controller] response: %s", resp)
        return json_format.MessageToDict(
            resp,
            preserving_proto_field_name=True,
            use_integers_for_enums=True,
            including_default_value_fields=True,
        )

    def add_labels(self, user_id: int, new_labels: List, dry_run: bool) -> Dict:
        req = ControllerRequest(
            ExtraRequestType.add_label,
            user_id,
            args={"labels": new_labels, "dry_run": dry_run},
        )
        return self.send(req)

    def get_labels_of_user(self, user_id: int) -> List[str]:
        req = ControllerRequest(ExtraRequestType.get_label, user_id)
        resp = self.send(req)
        return list(resp["csv_labels"])

    def create_task(
        self,
        user_id: int,
        project_id: int,
        task_id: str,
        task_type: TaskType,
        task_parameters: Optional[Dict],
    ) -> Dict:
        req = ControllerRequest(task_type, user_id, project_id, task_id, args=task_parameters)
        return self.send(req)

    def terminate_task(self, user_id: int, task_hash: str, task_type: int) -> Dict:
        # parse project_id from task_hash
        project_id = TaskId.from_task_id(task_hash).repo_id

        req = ControllerRequest(
            ExtraRequestType.kill,
            user_id=user_id,
            project_id=project_id,
            args={
                "target_container": task_hash,
                "task_type": task_type,
            },
        )
        resp = self.send(req)
        return resp

    def pull_docker_image(self, url: str, user_id: int) -> Dict:
        req = ControllerRequest(
            ExtraRequestType.pull_image,
            user_id=user_id,
            args={"url": url},
        )
        return self.send(req)

    def get_gpu_info(self, user_id: int) -> Dict[str, int]:
        req = ControllerRequest(
            ExtraRequestType.get_gpu_info,
            user_id=user_id,
        )
        resp = self.send(req)
        return {"gpu_count": resp["available_gpu_counts"]}

    def create_user(self, user_id: int) -> Dict:
        req = ControllerRequest(ExtraRequestType.create_user, user_id=user_id)
        return self.send(req)

    def create_project(self, user_id: int, project_id: int, task_id: str, args: Dict) -> Dict:
        req = ControllerRequest(
            ExtraRequestType.create_project,
            user_id=user_id,
            project_id=project_id,
            task_id=task_id,
            args=args,
        )
        return self.send(req)

    def import_dataset(self, user_id: int, project_id: int, task_hash: str, task_type: Any, args: Dict) -> Dict:
        req = ControllerRequest(
            TaskType(task_type),
            user_id=user_id,
            project_id=project_id,
            task_id=task_hash,
            args=args,
        )
        return self.send(req)

    def call_inference(
        self,
        user_id: int,
        model_hash: Optional[str],
        asset_dir: str,
        docker_image: Optional[str],
        docker_config: Optional[str],
    ) -> Dict:
        if None in (model_hash, docker_image, docker_config):
            raise ValueError("Missing model or docker image")
        req = ControllerRequest(
            ExtraRequestType.inference,
            user_id=user_id,
            args={
                "model_hash": model_hash,
                "asset_dir": asset_dir,
                "docker_image": docker_image,
                "docker_config": docker_config,
            },
        )
        return self.send(req)

    def create_data_fusion(
        self,
        user_id: int,
        project_id: int,
        task_id: str,
        task_parameters: Optional[Dict],
    ) -> Dict:
        req = ControllerRequest(TaskType.data_fusion, user_id, project_id, task_id, args=task_parameters)

        return self.send(req)

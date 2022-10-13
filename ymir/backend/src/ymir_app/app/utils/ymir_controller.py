import enum
import itertools
import secrets
import time
from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional, Union

import grpc
from fastapi.logger import logger
from google.protobuf.json_format import MessageToDict
from google.protobuf.text_format import MessageToString

from app.config import settings
from app.constants.state import TaskType, AnnotationType
from app.schemas.dataset import ImportStrategy, MergeStrategy
from app.schemas.task import TrainingDatasetsStrategy
from common_utils.labels import UserLabels, userlabels_to_proto
from id_definition.task_id import TaskId
from mir.protos import mir_command_pb2 as mir_cmd_pb
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
    evaluate = 603
    check_repo = 604
    fix_repo = 605
    get_cmd_version = 606


MERGE_STRATEGY_MAPPING = {
    MergeStrategy.stop_upon_conflict: mirsvrpb.MergeStrategy.STOP,
    MergeStrategy.prefer_newest: mirsvrpb.MergeStrategy.HOST,
    MergeStrategy.prefer_oldest: mirsvrpb.MergeStrategy.HOST,
}


TRAINING_DATASET_STRATEGY_MAPPING = {
    TrainingDatasetsStrategy.stop: mirsvrpb.MergeStrategy.STOP,
    TrainingDatasetsStrategy.as_training: mirsvrpb.MergeStrategy.HOST,
    TrainingDatasetsStrategy.as_validation: mirsvrpb.MergeStrategy.GUEST,
}


IMPORTING_STRATEGY_MAPPING = {
    ImportStrategy.no_annotations: mirsvrpb.UnknownTypesStrategy.UTS_IGNORE,
    ImportStrategy.ignore_unknown_annotations: mirsvrpb.UnknownTypesStrategy.UTS_IGNORE,
    ImportStrategy.stop_upon_unknown_annotations: mirsvrpb.UnknownTypesStrategy.UTS_STOP,
    ImportStrategy.add_unknown_annotations: mirsvrpb.UnknownTypesStrategy.UTS_ADD,
}

ANNOTATION_TYPE_MAPPING = {
    AnnotationType.gt: mirsvrpb.AnnotationType.GT,
    AnnotationType.pred: mirsvrpb.AnnotationType.PRED,
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
    archived_task_parameters: Optional[str] = None

    def __post_init__(self) -> None:
        user_hash = gen_user_hash(self.user_id)
        repo_hash = gen_repo_hash(self.project_id)
        task_hash = self.task_id or gen_task_hash(self.user_id, self.project_id)

        request = mirsvrpb.GeneralReq(
            user_id=user_hash, repo_id=repo_hash, task_id=task_hash, task_parameters=self.archived_task_parameters
        )

        method_name = "prepare_" + self.type.name
        self.req = getattr(self, method_name)(request, self.args)

    def prepare_create_user(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.USER_CREATE
        return request

    def prepare_create_project(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.REPO_CREATE
        return request

    def prepare_training(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.in_class_ids[:] = args["class_ids"]
        train_task_req = mirsvrpb.TaskReqTraining()
        datasets = itertools.chain(
            gen_typed_datasets(mir_cmd_pb.TvtTypeTraining, [args["dataset_hash"]]),
            gen_typed_datasets(mir_cmd_pb.TvtTypeValidation, [args["validation_dataset_hash"]]),
        )
        for dataset in datasets:
            train_task_req.in_dataset_types.append(dataset)
        if args.get("preprocess"):
            train_task_req.preprocess_config = args["preprocess"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_cmd_pb.TaskType.TaskTypeTraining
        req_create_task.training.CopyFrom(train_task_req)

        if args.get("model_hash"):
            request.model_hash = args["model_hash"]
            request.model_stage = args["model_stage_name"]
        request.req_type = mirsvrpb.RequestType.TASK_CREATE
        request.singleton_op = args["docker_image"]
        request.docker_image_config = args["docker_config"]
        # stop if training_dataset and validation_dataset share any assets
        request.merge_strategy = TRAINING_DATASET_STRATEGY_MAPPING[args["strategy"]]
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_mining(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.in_dataset_ids[:] = [args["dataset_hash"]]
        mine_task_req = mirsvrpb.TaskReqMining()
        if args.get("top_k"):
            mine_task_req.top_k = args["top_k"]
        mine_task_req.generate_annotations = args["generate_annotations"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_cmd_pb.TaskType.TaskTypeMining
        req_create_task.mining.CopyFrom(mine_task_req)

        request.req_type = mirsvrpb.RequestType.TASK_CREATE
        request.singleton_op = args["docker_image"]
        request.docker_image_config = args["docker_config"]
        request.model_hash = args["model_hash"]
        request.model_stage = args["model_stage_name"]
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_import_data(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        import_dataset_request = mirsvrpb.TaskReqImportDataset()

        import_dataset_request.asset_dir = args["asset_dir"]
        strategy = args.get("strategy") or ImportStrategy.ignore_unknown_annotations
        if strategy != ImportStrategy.no_annotations:
            if args.get("gt_dir"):
                import_dataset_request.gt_dir = args["gt_dir"]
            if args.get("pred_dir"):
                import_dataset_request.pred_dir = args["pred_dir"]
        import_dataset_request.clean_dirs = args["clean_dirs"]

        import_dataset_request.unknown_types_strategy = IMPORTING_STRATEGY_MAPPING[strategy]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_cmd_pb.TaskType.TaskTypeImportData
        req_create_task.import_dataset.CopyFrom(import_dataset_request)

        request.req_type = mirsvrpb.RequestType.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_label(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.in_dataset_ids[:] = [args["dataset_hash"]]
        request.in_class_ids[:] = args["class_ids"]
        label_request = mirsvrpb.TaskReqLabeling()
        label_request.project_name = f"label_${args['dataset_name']}"
        label_request.labeler_accounts[:] = args["labellers"]

        # pre annotation
        if args.get("annotation_type"):
            label_request.annotation_type = ANNOTATION_TYPE_MAPPING[args["annotation_type"]]

        if args.get("extra_url"):
            label_request.expert_instruction_url = args["extra_url"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_cmd_pb.TaskType.TaskTypeLabel
        req_create_task.labeling.CopyFrom(label_request)

        request.req_type = mirsvrpb.RequestType.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_copy_data(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.in_dataset_ids[:] = [args["src_resource_id"]]
        copy_request = mirsvrpb.TaskReqCopyData()
        strategy = args.get("strategy") or ImportStrategy.ignore_unknown_annotations
        if strategy is ImportStrategy.ignore_unknown_annotations:
            copy_request.name_strategy_ignore = True
        elif strategy is ImportStrategy.stop_upon_unknown_annotations:
            copy_request.name_strategy_ignore = False
        elif strategy is ImportStrategy.no_annotations:
            copy_request.drop_annotations = True
        else:
            raise ValueError("not supported strategy: %s" % strategy.name)

        copy_request.src_user_id = args["src_user_id"]
        copy_request.src_repo_id = args["src_repo_id"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_cmd_pb.TaskType.TaskTypeCopyData
        req_create_task.copy.CopyFrom(copy_request)

        request.req_type = mirsvrpb.RequestType.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_inference(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_INFERENCE
        request.model_hash = args["model_hash"]
        request.model_stage = args["model_stage_name"]
        request.asset_dir = args["asset_dir"]
        request.singleton_op = args["docker_image"]
        request.docker_image_config = args["docker_config"]
        return request

    def prepare_add_label(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.check_only = args["dry_run"]
        request.req_type = mirsvrpb.CMD_LABEL_ADD
        request.label_collection.CopyFrom(userlabels_to_proto(args["labels"]))
        return request

    def prepare_get_label(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_LABEL_GET
        return request

    def prepare_kill(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_TERMINATE
        request.executant_name = args["target_container"]
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
        request.in_dataset_ids[:] = args["include_datasets"]
        request.merge_strategy = MERGE_STRATEGY_MAPPING[args.get("strategy", MergeStrategy.stop_upon_conflict)]
        if args.get("exclude_datasets"):
            request.ex_dataset_ids[:] = args["exclude_datasets"]

        if args.get("include_class_ids"):
            request.in_class_ids[:] = args["include_class_ids"]
        if args.get("exclude_class_ids"):
            request.ex_class_ids[:] = args["exclude_class_ids"]

        if args.get("sampling_count"):
            request.sampling_count = args["sampling_count"]
        else:
            # not sampling
            request.sampling_rate = 1

        req_create_task = mirsvrpb.ReqCreateTask()

        req_create_task.task_type = mir_cmd_pb.TaskType.TaskTypeFusion

        request.req_type = mirsvrpb.RequestType.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_import_model(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        import_model_request = mirsvrpb.TaskReqImportModel()
        import_model_request.model_package_path = args["model_package_path"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_cmd_pb.TaskType.TaskTypeImportModel
        req_create_task.import_model.CopyFrom(import_model_request)

        request.req_type = mirsvrpb.RequestType.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)

        return request

    def prepare_copy_model(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        copy_request = mirsvrpb.TaskReqCopyData()
        copy_request.src_user_id = args["src_user_id"]
        copy_request.src_repo_id = args["src_repo_id"]
        request.in_dataset_ids[:] = [args["src_resource_id"]]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_cmd_pb.TaskType.TaskTypeCopyModel
        req_create_task.copy.CopyFrom(copy_request)

        request.req_type = mirsvrpb.RequestType.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)

        return request

    def prepare_dataset_infer(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        # need different app type for web, controller use same endpoint
        return self.prepare_mining(request, args)

    def prepare_evaluate(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        evaluate_config = mir_cmd_pb.EvaluateConfig()
        evaluate_config.conf_thr = args["confidence_threshold"]
        evaluate_config.iou_thrs_interval = args["iou_thrs_interval"]
        evaluate_config.need_pr_curve = args["need_pr_curve"]
        if args.get("main_ck"):
            evaluate_config.main_ck = args["main_ck"]

        request.req_type = mirsvrpb.CMD_EVALUATE
        request.in_dataset_ids[:] = [args["dataset_hash"]]
        request.evaluate_config.CopyFrom(evaluate_config)
        return request

    def prepare_check_repo(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_REPO_CHECK
        return request

    def prepare_fix_repo(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_REPO_CLEAR
        return request

    def prepare_get_cmd_version(self, request: mirsvrpb.GeneralReq, args: Dict) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_VERSIONS_GET
        return request


class ControllerClient:
    def __init__(self, channel: str = settings.GRPC_CHANNEL) -> None:
        self.channel_ep = channel

    def close(self) -> None:
        pass

    def send(self, req: mirsvrpb.GeneralReq, verbose: bool = True) -> Dict:
        logger.info("[controller] request: %s", req.req)
        with grpc.insecure_channel(self.channel_ep) as channel:
            stub = mir_grpc.mir_controller_serviceStub(channel)
            resp = stub.data_manage_request(req.req)

        if resp.code != 0:
            raise ValueError(f"gRPC error. response: {resp.code} {resp.message}")
        msg = "[controller] successfully get response"
        if verbose:
            msg = "%s: %s" % (msg, MessageToString(resp, as_one_line=True))
        logger.info(msg)
        return MessageToDict(
            resp,
            preserving_proto_field_name=True,
            use_integers_for_enums=True,
            including_default_value_fields=True,
        )

    def add_labels(self, user_id: int, new_labels: UserLabels, dry_run: bool) -> Dict:
        req = ControllerRequest(
            ExtraRequestType.add_label,
            user_id,
            args={"labels": new_labels, "dry_run": dry_run},
        )
        return self.send(req)

    def get_labels_of_user(self, user_id: int) -> UserLabels:
        req = ControllerRequest(ExtraRequestType.get_label, user_id)
        resp = self.send(req, verbose=False)
        # if not set labels, lost the key label_collection
        if not resp.get("label_collection"):
            raise ValueError(f"Missing labels for user {user_id}")
        return UserLabels.parse_obj(
            dict(
                labels=resp["label_collection"]["labels"],
                ymir_version=resp["label_collection"]["ymir_version"],
            )
        )

    def create_task(
        self,
        user_id: int,
        project_id: int,
        task_id: str,
        task_type: TaskType,
        args: Optional[Dict],
        archived_task_parameters: Optional[str],
    ) -> Dict:
        req = ControllerRequest(
            type=TaskType(task_type),
            user_id=user_id,
            project_id=project_id,
            task_id=task_id,
            args=args,
            archived_task_parameters=archived_task_parameters,
        )
        return self.send(req)

    def terminate_task(self, user_id: int, task_hash: str, task_type: int) -> Dict:
        # parse project_id from task_hash
        project_id = TaskId.from_task_id(task_hash).repo_id

        req = ControllerRequest(
            type=ExtraRequestType.kill,
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
            type=ExtraRequestType.pull_image,
            user_id=user_id,
            args={"url": url},
        )
        return self.send(req)

    def get_gpu_info(self, user_id: int) -> Dict[str, int]:
        req = ControllerRequest(
            type=ExtraRequestType.get_gpu_info,
            user_id=user_id,
        )
        resp = self.send(req)
        return {"gpu_count": resp["available_gpu_counts"]}

    def create_user(self, user_id: int) -> Dict:
        req = ControllerRequest(type=ExtraRequestType.create_user, user_id=user_id)
        return self.send(req)

    def create_project(self, user_id: int, project_id: int, task_id: str) -> Dict:
        req = ControllerRequest(
            type=ExtraRequestType.create_project,
            user_id=user_id,
            project_id=project_id,
            task_id=task_id,
        )
        return self.send(req)

    def import_dataset(self, user_id: int, project_id: int, task_hash: str, task_type: Any, args: Dict) -> Dict:
        req = ControllerRequest(
            type=TaskType(task_type),
            user_id=user_id,
            project_id=project_id,
            task_id=task_hash,
            args=args,
        )
        return self.send(req)

    def call_inference(
        self,
        user_id: int,
        project_id: int,
        model_hash: Optional[str],
        model_stage_name: Optional[str],
        asset_dir: str,
        docker_image: Optional[str],
        docker_config: Optional[str],
    ) -> Dict:
        if None in (model_hash, docker_image, docker_config):
            raise ValueError("Missing model or docker image")
        req = ControllerRequest(
            type=ExtraRequestType.inference,
            user_id=user_id,
            project_id=project_id,
            args={
                "model_hash": model_hash,
                "model_stage_name": model_stage_name,
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
        args: Optional[Dict],
    ) -> Dict:
        req = ControllerRequest(
            type=TaskType.data_fusion, user_id=user_id, project_id=project_id, task_id=task_id, args=args
        )

        return self.send(req)

    def import_model(self, user_id: int, project_id: int, task_id: str, task_type: Any, args: Dict) -> Dict:
        req = ControllerRequest(
            type=task_type,
            user_id=user_id,
            project_id=project_id,
            task_id=task_id,
            args=args,
        )
        return self.send(req)

    def evaluate_dataset(
        self,
        user_id: int,
        project_id: int,
        user_labels: UserLabels,
        confidence_threshold: float,
        iou_thrs_interval: str,
        need_pr_curve: bool,
        main_ck: Optional[str],
        dataset_hash: str,
    ) -> Dict:
        req = ControllerRequest(
            type=ExtraRequestType.evaluate,
            user_id=user_id,
            project_id=project_id,
            args={
                "confidence_threshold": confidence_threshold,
                "dataset_hash": dataset_hash,
                "iou_thrs_interval": iou_thrs_interval,
                "need_pr_curve": need_pr_curve,
                "main_ck": main_ck,
            },
        )
        resp = self.send(req)
        evaluation_result = resp["evaluation"]
        convert_class_id_to_keyword(evaluation_result, user_labels)
        return {dataset_hash: evaluation_result}

    def check_repo_status(self, user_id: int, project_id: int) -> bool:
        req = ControllerRequest(
            type=ExtraRequestType.check_repo,
            user_id=user_id,
            project_id=project_id,
        )
        resp = self.send(req)
        return resp["ops_ret"]

    def fix_repo(self, user_id: int, project_id: int) -> Dict:
        req = ControllerRequest(
            type=ExtraRequestType.fix_repo,
            user_id=user_id,
            project_id=project_id,
        )
        return self.send(req)

    def merge_datasets(
        self,
        user_id: int,
        project_id: int,
        task_id: str,
        dataset_hashes: Optional[List[str]],
        ex_dataset_hashes: Optional[List[str]],
        merge_strategy: Optional[MergeStrategy] = None,
    ) -> Dict:
        req = ControllerRequest(
            type=TaskType.data_fusion,
            user_id=user_id,
            project_id=project_id,
            task_id=task_id,
            args={
                "include_datasets": dataset_hashes,
                "exclude_datasets": ex_dataset_hashes,
                "strategy": merge_strategy,
            },
        )
        return self.send(req)

    def filter_dataset(
        self,
        user_id: int,
        project_id: int,
        task_id: str,
        dataset_hash: str,
        class_ids: Optional[List[int]],
        ex_class_ids: Optional[List[int]],
        sampling_count: Optional[int] = None,
    ) -> Dict:
        req = ControllerRequest(
            type=TaskType.data_fusion,
            user_id=user_id,
            project_id=project_id,
            task_id=task_id,
            args={
                "include_datasets": [dataset_hash],
                "include_class_ids": class_ids,
                "exclude_class_ids": ex_class_ids,
                "sampling_count": sampling_count,
            },
        )
        return self.send(req)

    def get_cmd_version(self) -> List[str]:
        req = ControllerRequest(type=ExtraRequestType.get_cmd_version, user_id=0)
        resp = self.send(req)
        return resp["sandbox_versions"]


def convert_class_id_to_keyword(obj: Dict, user_labels: UserLabels) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "ci_evaluations":
                obj[key] = {user_labels.main_name_for_id(k): v for k, v in value.items()}
            else:
                convert_class_id_to_keyword(obj[key], user_labels)

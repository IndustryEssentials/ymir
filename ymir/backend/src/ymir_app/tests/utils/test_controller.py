import random

import pytest

from app.schemas.common import MergeStrategy
from app.utils import ymir_controller as m
from tests.utils.utils import random_lower_string, random_url


def test_gen_typed_datasets():
    dataset_type = random.randint(1, 3)
    dataset_hashes = [random_lower_string() for _ in range(10)]
    typed_datasets = [{"type": dataset_type, "hash": _hash} for _hash in dataset_hashes]
    res = m.gen_typed_datasets(typed_datasets)
    for dataset in res:
        assert dataset.dataset_type == dataset_type


class TestControllerRequest:
    def test_training(self):
        task_type = m.TaskType.training
        user_id = random.randint(1000, 2000)
        project_id = random.randint(1000, 2000)
        ret = m.ControllerRequest(
            task_type,
            user_id,
            project_id,
            args={
                "typed_labels": [],
                "typed_datasets": [],
                "typed_models": [],
                "merge_strategy": MergeStrategy.prefer_newest,
                "docker_image": "yolov4-training:test",
                "docker_image_config": "{}",
            },
        )
        assert ret.req.req_type == m.mirsvrpb.RequestType.TASK_CREATE
        assert ret.req.req_create_task.task_type == m.mir_cmd_pb.TaskType.TaskTypeTraining

    def test_mining(self):
        task_type = m.TaskType.mining
        user_id = random.randint(1000, 2000)
        project_id = random.randint(1000, 2000)
        ret = m.ControllerRequest(
            task_type,
            user_id,
            project_id,
            args={
                "typed_labels": [],
                "typed_datasets": [],
                "typed_models": [{"hash": random_lower_string(), "stage_name": random_lower_string()}],
                "top_k": 1000,
                "generate_annotations": True,
                "merge_strategy": MergeStrategy.prefer_newest,
                "docker_image": "yolov4-training:test",
                "docker_image_config": "{}",
            },
        )
        assert ret.req.req_type == m.mirsvrpb.RequestType.TASK_CREATE
        assert ret.req.req_create_task.task_type == m.mir_cmd_pb.TaskType.TaskTypeMining

    def test_label(self):
        task_type = m.TaskType.label
        user_id = random.randint(1000, 2000)
        project_id = random.randint(1000, 2000)
        ret = m.ControllerRequest(
            task_type,
            user_id,
            project_id,
            args={
                "typed_labels": [],
                "typed_datasets": [{"name": random_lower_string(), "hash": random_lower_string()}],
                "labellers": [],
                "extra_url": random_url(),
                "annotation_type": 2,
                "object_type": 3,
            },
        )
        assert ret.req.req_type == m.mirsvrpb.RequestType.TASK_CREATE
        assert ret.req.req_create_task.task_type == m.mir_cmd_pb.TaskType.TaskTypeLabel
        assert ret.req.req_create_task.labeling.annotation_type == m.mir_cmd_pb.AnnotationType.AT_PRED

    def test_copy_data(self):
        task_type = m.TaskType.copy_data
        user_id = random.randint(1000, 2000)
        project_id = random.randint(1000, 2000)
        ret = m.ControllerRequest(
            task_type,
            user_id,
            project_id,
            args={
                "src_user_id": f"{random.randint(1000, 2000):0>4}",
                "src_repo_id": random_lower_string(),
                "src_resource_id": random_lower_string(),
            },
        )
        assert ret.req.req_type == m.mirsvrpb.RequestType.TASK_CREATE
        assert ret.req.req_create_task.task_type == m.mir_cmd_pb.TaskType.TaskTypeCopyData

    def test_kill(self, mocker):
        task_type = m.ExtraRequestType.kill
        user_id = random.randint(1000, 2000)
        project_id = random.randint(1000, 2000)
        task = mocker.Mock(hash=random_lower_string(), type=m.TaskType.label)

        kill_other_task = m.ControllerRequest(
            task_type,
            user_id,
            project_id,
            args={"target_container": task.hash, "task_type": task.type},
        )
        assert kill_other_task.req.req_type == m.mirsvrpb.CMD_TERMINATE
        assert kill_other_task.req.terminated_task_type == task.type
        assert kill_other_task.req.executant_name == task.hash


class TestControllerClient:
    def test_send_with_grpc_error(self, mocker):
        channel_str = random_lower_string()

        mock_grpc = mocker.Mock()
        mocker.patch.object(m, "grpc", return_value=mock_grpc)

        mock_mir_grpc = mocker.Mock()
        mock_mir_grpc.mir_controller_serviceStub().data_manage_request.return_value = mocker.Mock(code=-1)
        mocker.patch.object(m, "mir_grpc", mock_mir_grpc)

        cc = m.ControllerClient(channel_str)
        req = mocker.Mock()
        with pytest.raises(ValueError):
            cc.send(req)

    def test_send(self, mocker):
        channel_str = random_lower_string()

        mock_grpc = mocker.Mock()
        mocker.patch.object(m, "grpc", return_value=mock_grpc)

        mock_mir_grpc = mocker.Mock()
        mock_mir_grpc.mir_controller_serviceStub().data_manage_request.return_value = mocker.Mock(code=0)
        mocker.patch.object(m, "mir_grpc", mock_mir_grpc)

        cc = m.ControllerClient(channel_str)
        req = mocker.Mock()
        mocker.patch.object(m, "MessageToDict")
        mocker.patch.object(m, "MessageToString")
        cc.send(req)

    def test_inference(self, mocker):
        user_id = random.randint(1000, 9000)
        project_id = random.randint(1000, 9000)
        model_hash = random_lower_string()
        model_stage = random_lower_string()
        asset_dir = random_lower_string()
        channel_str = random_lower_string()
        docker_image = random_lower_string()
        docker_config = random_lower_string()
        cc = m.ControllerClient(channel_str)
        cc.send = mock_send = mocker.Mock()
        cc.call_inference(user_id, project_id, model_hash, model_stage, asset_dir, docker_image, docker_config)
        mock_send.assert_called()
        generated_req = mock_send.call_args[0][0].req
        assert generated_req.user_id == str(user_id)
        assert generated_req.model_hash == model_hash
        assert generated_req.asset_dir == asset_dir
        assert generated_req.singleton_op == docker_image
        assert generated_req.docker_image_config == docker_config

    def test_evaluate(self, mocker):
        user_id = random.randint(1000, 9000)
        project_id = random.randint(1000, 9000)
        channel_str = random_lower_string()
        user_labels = mocker.Mock()
        confidence_threshold, iou_thrs_interval, need_pr_curve = 0.5, "0.5", True
        main_ck = None
        is_instance_segmentation = True
        dataset_hash = random_lower_string()
        cc = m.ControllerClient(channel_str)
        mock_convertor = mocker.Mock()
        mocker.patch.object(m, "convert_class_id_to_keyword", mock_convertor)
        resp = {"evaluation": mocker.Mock()}
        cc.send = mocker.Mock(return_value=resp)
        cc.evaluate_prediction(
            user_id,
            project_id,
            user_labels,
            confidence_threshold,
            iou_thrs_interval,
            need_pr_curve,
            main_ck,
            is_instance_segmentation,
            dataset_hash,
        )
        mock_convertor.assert_called()

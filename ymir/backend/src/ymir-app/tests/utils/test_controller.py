import random

import pytest

from app.utils import ymir_controller as m
from tests.utils.utils import random_lower_string, random_url


def test_gen_typed_datasets():
    dataset_type = random.randint(1, 3)
    dataset_ids = [random_lower_string() for _ in range(10)]
    res = m.gen_typed_datasets(dataset_type, dataset_ids)
    for dataset in res:
        assert dataset.dataset_type == dataset_type


class TestControllerRequest:
    def test_filter(self):
        task_type = m.TaskType.filter
        user_id = random.randint(1000, 2000)

        include_datasets = [random_lower_string() for _ in range(10)]
        include_classes = [random.randint(1, 80) for _ in range(10)]
        exclude_classes = [random.randint(1, 80) for _ in range(10)]

        ret = m.ControllerRequest(
            task_type,
            user_id,
            args={
                "include_datasets": include_datasets,
                "include_classes": include_classes,
                "exclude_classes": exclude_classes,
                "strategy": m.MergeStrategy.prefer_newest,
            },
        )
        assert ret.req.req_type == m.mirsvrpb.TASK_CREATE
        assert ret.req.req_create_task.task_type == m.mirsvrpb.TaskTypeFilter

    def test_training(self):
        task_type = m.TaskType.training
        user_id = random.randint(1000, 2000)
        ret = m.ControllerRequest(
            task_type,
            user_id,
            args={
                "include_train_datasets": [],
                "include_validation_datasets": [],
                "include_test_datasets": [],
                "include_classes": [],
                "strategy": m.MergeStrategy.prefer_newest,
                "docker_image": "yolov4-training:test",
                "docker_config": "{}",
            },
        )
        assert ret.req.req_type == m.mirsvrpb.TASK_CREATE
        assert ret.req.req_create_task.task_type == m.mirsvrpb.TaskTypeTraining

    def test_mining(self):
        task_type = m.TaskType.mining
        user_id = random.randint(1000, 2000)
        ret = m.ControllerRequest(
            task_type,
            user_id,
            args={
                "top_k": 1000,
                "model_hash": random_lower_string(),
                "include_datasets": [],
                "ex_dataset_ids": [],
                "generate_annotations": True,
                "strategy": m.MergeStrategy.prefer_newest,
                "docker_image": "yolov4-training:test",
                "docker_config": "{}",
            },
        )
        assert ret.req.req_type == m.mirsvrpb.TASK_CREATE
        assert ret.req.req_create_task.task_type == m.mirsvrpb.TaskTypeMining

    def test_label(self):
        task_type = m.TaskType.label
        user_id = random.randint(1000, 2000)
        ret = m.ControllerRequest(
            task_type,
            user_id,
            args={
                "name": random_lower_string(),
                "include_datasets": [random_lower_string()],
                "labellers": [],
                "include_classes": [],
                "extra_url": random_url(),
                "keep_annotations": True,
            },
        )
        assert ret.req.req_type == m.mirsvrpb.TASK_CREATE
        assert ret.req.req_create_task.task_type == m.mirsvrpb.TaskTypeLabel
        assert ret.req.req_create_task.labeling.export_annotation

    def test_copy_data(self):
        task_type = m.TaskType.copy_data
        user_id = random.randint(1000, 2000)
        ret = m.ControllerRequest(
            task_type,
            user_id,
            args={
                "src_user_id": f"{random.randint(1000, 2000):0>4}",
                "src_repo_id": random_lower_string(),
                "src_dataset_id": random_lower_string(),
            },
        )
        assert ret.req.req_type == m.mirsvrpb.TASK_CREATE
        assert ret.req.req_create_task.task_type == m.mirsvrpb.TaskTypeCopyData

    def test_kill(self, mocker):
        task_type = m.ExtraRequestType.kill
        user_id = random.randint(1000, 2000)
        task = mocker.Mock(hash=random_lower_string(), type=m.TaskType.label)

        kill_other_task = m.ControllerRequest(
            task_type,
            user_id,
            args={"target_container": task.hash, "task_type": task.type},
        )
        assert kill_other_task.req.req_type == m.mirsvrpb.CMD_TERMINATE
        assert kill_other_task.req.terminated_task_type == task.type
        assert kill_other_task.req.executor_instance == task.hash


class TestControllerClient:
    def test_close_controller(self, mocker):
        channel_str = random_lower_string()
        mock_grpc = mocker.Mock()
        mocker.patch.object(m, "grpc", return_value=mock_grpc)
        cc = m.ControllerClient(channel_str)
        cc.channel = mock_channel = mocker.Mock()
        cc.close()
        mock_channel.close.assert_called()

    def test_send_with_grpc_error(self, mocker):
        channel_str = random_lower_string()
        cc = m.ControllerClient(channel_str)
        mock_stub = mocker.Mock()
        mock_stub.data_manage_request.return_value = mocker.Mock(code=-1)
        cc.stub = mock_stub
        req = mocker.Mock()
        with pytest.raises(ValueError):
            cc.send(req)

    def test_send(self, mocker):
        channel_str = random_lower_string()
        cc = m.ControllerClient(channel_str)
        mock_stub = mocker.Mock()
        mock_stub.data_manage_request.return_value = mocker.Mock(code=0)
        cc.stub = mock_stub
        req = mocker.Mock()
        mocker.patch.object(m, "json_format")
        cc.send(req)
        mock_stub.data_manage_request.assert_called()

    def test_inference(self, mocker):
        user_id = random.randint(1000, 9000)
        model_hash = random_lower_string()
        asset_dir = random_lower_string()
        channel_str = random_lower_string()
        docker_image = random_lower_string()
        docker_config = random_lower_string()
        cc = m.ControllerClient(channel_str)
        cc.send = mock_send = mocker.Mock()
        cc.call_inference(user_id, model_hash, asset_dir, docker_image, docker_config)
        mock_send.assert_called()
        generated_req = mock_send.call_args[0][0].req
        assert generated_req.user_id == str(user_id)
        assert generated_req.model_hash == model_hash
        assert generated_req.asset_dir == asset_dir
        assert generated_req.singleton_op == docker_image
        assert generated_req.docker_image_config == docker_config

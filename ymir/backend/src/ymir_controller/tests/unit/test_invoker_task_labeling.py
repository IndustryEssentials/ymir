import json
import logging
import os
import shutil
from pathlib import Path
from unittest import mock

import pytest
import requests

import tests.utils as test_utils
from common_utils import labels
from controller.invoker.invoker_task_exporting import TaskExportingInvoker
from controller.label_model import label_studio
from controller.label_model.label_free import LabelFree
from controller.utils import utils
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from proto import backend_pb2


@pytest.fixture()
def mock_many(mocker):
    mocker.patch.object(TaskExportingInvoker, "exporting_cmd")
    mocker.patch("builtins.open", mocker.mock_open(read_data="data"))
    mocker.patch("os.listdir", return_value=[])
    mocker.patch.object(Path, "touch")
    labels.UserLabels.get_main_names = mock.Mock(return_value=["fake"])


class TestTaskLabelingInvoker:
    def test_task_invoke(self, mocker, mock_many):
        label_req = backend_pb2.TaskReqLabeling()
        label_req.in_class_ids[:] = [0, 1]
        label_req.labeler_accounts[:] = ["a@a.com"]
        label_req.project_name = "fake_project_name"
        label_req.dataset_id = "id"
        label_req.expert_instruction_url = "url"
        label_req.export_annotation = False

        req_create_task = backend_pb2.ReqCreateTask()
        req_create_task.task_type = backend_pb2.TaskTypeLabel
        req_create_task.labeling.CopyFrom(label_req)
        req_create_task.no_task_monitor = True

        mock_resp = mocker.Mock()
        mock_resp.raise_for_status = mocker.Mock()
        mock_resp.status_code = 200
        mock_resp.json = {"id": 1}
        mock_resp.content = json.dumps({"id": 1})

        mock_post = mocker.patch.object(requests, "post", return_value=mock_resp)

        sandbox_root = test_utils.dir_test_root(["test_invoker_labeling"])
        user_name = "user"
        mir_repo_name = "repoid"
        task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzb5'
        user_root = os.path.join(sandbox_root, user_name)
        mir_repo_root = os.path.join(user_root, mir_repo_name)
        if os.path.isdir(mir_repo_root):
            logging.info("mir_repo_root exists, remove it first")
            shutil.rmtree(mir_repo_root)
        os.makedirs(mir_repo_root)
        test_utils.mir_repo_init(mir_repo_root)

        working_dir = os.path.join(sandbox_root, "work_dir", backend_pb2.TaskType.Name(backend_pb2.TaskTypeLabel),
                                   task_id, 'sub_task', task_id)
        if os.path.isdir(working_dir):
            logging.info("working_dir exists, remove it first")
            shutil.rmtree(working_dir)
        os.makedirs(working_dir)
        response = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.TASK_CREATE],
                                         sandbox_root=sandbox_root,
                                         assets_config=dict(assetskvlocation="fake_assetskvlocation"),
                                         req_type=backend_pb2.TASK_CREATE,
                                         user_id=user_name,
                                         repo_id=mir_repo_name,
                                         task_id=task_id,
                                         req_create_task=req_create_task)
        assert mock_post.call_count == 4

        expected_ret = backend_pb2.GeneralResp()
        assert response == expected_ret

        mocker.patch.object(utils, "create_label_instance", return_value=LabelFree())
        response = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.TASK_CREATE],
                                         sandbox_root=sandbox_root,
                                         assets_config=dict(assetskvlocation="fake_assetskvlocation"),
                                         req_type=backend_pb2.TASK_CREATE,
                                         user_id=user_name,
                                         repo_id=mir_repo_name,
                                         task_id=task_id,
                                         req_create_task=req_create_task)
        assert mock_post.call_count == 8
        expected_ret = backend_pb2.GeneralResp()
        assert response == expected_ret

        shutil.rmtree(working_dir)
        shutil.rmtree(mir_repo_root)

    def test_get_task_completion_percent(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.raise_for_status = mocker.Mock()
        mock_resp.status_code = 200
        mock_resp.content = json.dumps({"num_tasks_with_annotations": 1, "task_number": 10})
        mocker.patch.object(requests, "get", return_value=mock_resp)

        res = label_studio.LabelStudio().get_task_completion_percent(1)

        assert res == 0.1

        res = LabelFree().get_task_completion_percent(1)
        assert res == 0.1

        mock_resp.content = json.dumps({"num_tasks_with_annotations": 0, "task_number": 0})
        mocker.patch.object(requests, "get", return_value=mock_resp)
        res = label_studio.LabelStudio().get_task_completion_percent(1)

        assert res == 1.0

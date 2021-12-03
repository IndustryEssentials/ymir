import json
import os
from pathlib import Path

import pytest
import requests

from controller.invoker.invoker_task_exporting import TaskExportingInvoker
from controller.invoker.invoker_task_labeling import TaskLabelingInvoker
from controller.label_model import label_studio
from controller.utils.labels import LabelFileHandler


@pytest.fixture()
def mock_many(mocker):
    mocker.patch.object(os, "makedirs")
    mocker.patch.object(TaskExportingInvoker, "exporting_cmd")
    mocker.patch("builtins.open", mocker.mock_open(read_data="data"))
    mocker.patch("os.listdir", return_value=[])
    mocker.patch.object(Path, "touch")
    mocker.patch.object(LabelFileHandler, "get_main_labels_by_ids", return_value=["fake"])


class Req:
    pass


class TestTaskLabelingInvoker:
    def test_task_invoke(self, mocker, mock_many):
        label_req = Req()
        label_req.in_class_ids = [0, 1]
        label_req.labeler_accounts = ["a@a.com"]
        label_req.project_name = "fake_project_name"
        label_req.dataset_id = "id"
        label_req.expert_instruction_url = "url"

        create_req = Req()
        create_req.labeling = label_req

        req = Req()
        req.task_id = "task_id"
        req.req_create_task = create_req

        mock_resp = mocker.Mock()
        mock_resp.raise_for_status = mocker.Mock()
        mock_resp.status_code = 200
        mock_resp.json = {"id": 1}
        mock_resp.content = json.dumps({"id": 1})

        mock_post = mocker.patch.object(requests, "post", return_value=mock_resp)

        TaskLabelingInvoker.task_invoke(
            sandbox_root="fake_sandbox_root",
            repo_root="fake_repo_root",
            assets_config=dict(assetskvlocation="fake_assetskvlocation"),
            working_dir="fake_working_dir",
            task_monitor_file="fake_task_monitor_file",
            request=req,
        )

        assert mock_post.call_count == 4

    def test_get_task_completion_percent(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.raise_for_status = mocker.Mock()
        mock_resp.status_code = 200
        mock_resp.content = json.dumps({"num_tasks_with_annotations": 1, "task_number": 10})
        mocker.patch.object(requests, "get", return_value=mock_resp)

        res = label_studio.LabelStudio().get_task_completion_percent(1)

        assert res == 0.1

        mock_resp.content = json.dumps({"num_tasks_with_annotations": 0, "task_number": 0})
        mocker.patch.object(requests, "get", return_value=mock_resp)
        res = label_studio.LabelStudio().get_task_completion_percent(1)

        assert res == 0

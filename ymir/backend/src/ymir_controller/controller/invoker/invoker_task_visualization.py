from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Dict, List

import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout

from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.invoker.invoker_task_exporting import TaskExportingInvoker
from controller.utils import utils
from proto import backend_pb2
from id_definition.error_codes import CTLResponseCode
from common_utils.labels import UserLabels
from controller.config.fiftyone_task import FIFTYONE_URL, FIFTYONE_TIMEOUT


class TaskVisualizationInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def subtask_weights(cls) -> List[float]:
        return [1.0]

    @classmethod
    def subtask_invoke_0(
        cls,
        sandbox_root: str,
        repo_root: str,
        assets_config: Dict[str, str],
        request: backend_pb2.GeneralReq,
        subtask_id: str,
        subtask_workdir: str,
        previous_subtask_id: str,
        user_labels: UserLabels,
    ) -> backend_pb2.GeneralResp:
        # export as PASCAL_VOC format
        visualization = request.req_create_task.visualization

        media_location = assets_config["assetskvlocation"]
        format_str = utils.annotation_format_str(backend_pb2.LabelFormat.PASCAL_VOC)

        f_export = partial(cls.export_single_dataset, repo_root, subtask_workdir, media_location, format_str)
        with ThreadPoolExecutor() as executor:
            res = executor.map(f_export, visualization.in_dataset_ids)
        dataset_export_dirs = list(res)

        # create fiftyone task
        payload = cls.prepare_fiftyone_payload(
            visualization.fiftyone_tid,
            visualization.in_dataset_pks,
            visualization.in_dataset_names,
            dataset_export_dirs
        )
        try:
            resp = requests.post(FIFTYONE_URL, json=payload, timeout=FIFTYONE_TIMEOUT)
        except (ConnectionError, HTTPError, Timeout):
            return utils.make_general_response(
                CTLResponseCode.INVOKER_VISUALIZATION_TASK_NETWORK_ERROR, "Failed to connect fiftyone service"
            )
        if not resp.ok:
            return utils.make_general_response(
                CTLResponseCode.INVOKER_VISUALIZATION_TASK_FIFTYONE_ERROR, "Failed to create fiftyone task"
            )
        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @staticmethod
    def export_single_dataset(repo_root: str, work_dir: str, media_location: str, fmt: str, dataset_id: str) -> str:
        # the following dir names are specified in ymir-doc
        dataset_export_dir = f"{work_dir}/{dataset_id}"
        dirs = {
            "asset_dir": f"{dataset_export_dir}/images",
            "annotation_dir": f"{dataset_export_dir}/annotations",
            "gt_dir": f"{dataset_export_dir}/groundtruth",
        }
        utils.ensure_dirs_exist(list(dirs.values()))
        TaskExportingInvoker.exporting_cmd(
            repo_root=repo_root,
            dataset_id=dataset_id,
            annotation_format=fmt,
            media_location=media_location,
            **dirs,  # type: ignore
        )
        return dataset_export_dir

    @staticmethod
    def prepare_fiftyone_payload(
        tid: str, dataset_pks: List[int], dataset_names: List[str], dataset_export_dirs: List[str]
    ) -> Dict:
        payload = {
            "tid": tid,
            "datas": [
                {"id": id_, "name": name, "data_dir": data_dir}
                for id_, name, data_dir in zip(dataset_pks, dataset_names, dataset_export_dirs)
            ],
        }
        return payload

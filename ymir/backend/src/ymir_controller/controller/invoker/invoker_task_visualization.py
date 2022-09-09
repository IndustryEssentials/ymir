from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Dict, List, Optional

import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout

from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.invoker.invoker_task_exporting import TaskExportingInvoker
from controller.utils import utils
from proto import backend_pb2
from id_definition.error_codes import CTLResponseCode
from common_utils.labels import UserLabels
from controller.config.fiftyone_task import FIFTYONE_HOST_URL, FIFTYONE_TIMEOUT, FIFTYONE_CONCURRENT_LIMIT


class TaskVisualizationInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def subtask_weights(cls) -> List[float]:
        return [1.0]

    @classmethod
    def subtask_invoke_0(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                         assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                         subtask_workdir: str, previous_subtask_id: Optional[str]) -> backend_pb2.GeneralResp:
        # export as PASCAL_VOC format
        visualization = request.req_create_task.visualization

        media_location = assets_config["assetskvlocation"]
        format_str = utils.annotation_format_str(backend_pb2.AnnoFormat.AF_DET_PASCAL_VOC)

        iou_thr = visualization.iou_thr
        conf_thr = visualization.conf_thr

        f_export = partial(cls.evaluate_and_export_single_dataset, repo_root, subtask_id, subtask_workdir,
                           media_location, format_str, iou_thr, conf_thr)
        with ThreadPoolExecutor(FIFTYONE_CONCURRENT_LIMIT) as executor:
            res = executor.map(f_export, visualization.in_dataset_ids)
        dataset_export_dirs = list(res)

        # create fiftyone task
        payload = cls.prepare_fiftyone_payload(
            visualization.vis_tool_id,
            visualization.in_dataset_ids,
            visualization.in_dataset_names,
            dataset_export_dirs,
        )
        url = f"{FIFTYONE_HOST_URL}/api/task/"
        try:
            resp = requests.post(url, json=payload, timeout=FIFTYONE_TIMEOUT)
        except (ConnectionError, HTTPError, Timeout):
            return utils.make_general_response(CTLResponseCode.INVOKER_VISUALIZATION_TASK_NETWORK_ERROR,
                                               "Failed to connect fiftyone service")
        if not resp.ok:
            return utils.make_general_response(CTLResponseCode.INVOKER_VISUALIZATION_TASK_FIFTYONE_ERROR,
                                               "Failed to create fiftyone task")
        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @staticmethod
    def evaluate_and_export_single_dataset(
        repo_root: str,
        task_id: str,
        work_dir: str,
        media_location: str,
        fmt: str,
        iou_thr: float,
        conf_thr: float,
        dataset_id: str,
    ) -> str:
        # evaluate and add fpfn
        evaluated_dataset_id_with_tid = f'{dataset_id}@{task_id}'
        TaskVisualizationInvoker.evaluate_cmd(repo_root=repo_root,
                                              src_dataset_id=dataset_id,
                                              dataset_id_with_tid=evaluated_dataset_id_with_tid,
                                              iou_thr=iou_thr,
                                              conf_thr=conf_thr)

        # export
        # the following dir names are specified in ymir-doc
        dataset_export_dir = f"{work_dir}/{dataset_id}"
        dirs = {
            "asset_dir": f"{dataset_export_dir}/images",
            "pred_dir": f"{dataset_export_dir}/annotations",
            "gt_dir": f"{dataset_export_dir}/groundtruth",
        }
        utils.ensure_dirs_exist(list(dirs.values()))
        TaskExportingInvoker.exporting_cmd(
            repo_root=repo_root,
            dataset_id_with_tid=evaluated_dataset_id_with_tid,
            annotation_format=fmt,
            media_location=media_location,
            **dirs,  # type: ignore
        )
        return dataset_export_dir

    @staticmethod
    def evaluate_cmd(repo_root: str, src_dataset_id: str, dataset_id_with_tid: str, iou_thr: float,
                     conf_thr: float) -> backend_pb2.GeneralResp:
        evaluate_cmd = [
            utils.mir_executable(), 'evaluate', '--root', repo_root, '--src-revs', f"{src_dataset_id}@{src_dataset_id}",
            '--dst-rev', dataset_id_with_tid, '--conf-thr', f"{conf_thr}", '--iou-thrs', f"{iou_thr}",
            '--calc-confusion-matrix'
        ]

        return utils.run_command(evaluate_cmd)

    @staticmethod
    def prepare_fiftyone_payload(tid: str, dataset_ids: List[int], dataset_names: List[str],
                                 dataset_export_dirs: List[str]) -> Dict:
        payload = {
            "tid":
            tid,
            "datas": [{
                "hash": hash_,
                "name": name,
                "data_dir": data_dir
            } for hash_, name, data_dir in zip(dataset_ids, dataset_names, dataset_export_dirs)],
        }
        return payload

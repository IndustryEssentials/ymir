import logging
import os
import shutil
from typing import Dict, List, Optional, Tuple
from common_utils.labels import UserLabels

from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.utils import utils
from id_definition.error_codes import CMDResponseCode, CTLResponseCode
from mir.protos import mir_command_pb2 as mir_cmd_pb
from proto import backend_pb2, backend_pb2_utils


class TaskImportDatasetInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        import_dataset_request = request.req_create_task.import_dataset
        (asset_dir, pred_dir, gt_dir) = (import_dataset_request.asset_dir, import_dataset_request.pred_dir,
                                         import_dataset_request.gt_dir)
        if pred_dir:
            if not os.access(pred_dir, os.R_OK):
                return utils.make_general_response(code=CMDResponseCode.RC_CMD_INVALID_DATASET,
                                                   message=f"invalid permissions of pred_dir: {pred_dir}")
        if gt_dir:
            if not os.access(gt_dir, os.R_OK):
                return utils.make_general_response(code=CMDResponseCode.RC_CMD_INVALID_DATASET,
                                                   message=f"invalid permissions of gt_dir: {gt_dir}")
        if not asset_dir:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message="empty asset_dir")
        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message="")

    @classmethod
    def register_subtasks(cls, request: backend_pb2.GeneralReq) -> List[Tuple[SubTaskType, float]]:
        return [(cls.subtask_invoke_import, 1.0)]

    @classmethod
    def subtask_invoke_import(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                              assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                              subtask_workdir: str, his_task_id: Optional[str],
                              in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        import_dataset_request = request.req_create_task.import_dataset
        import_dataset_response = cls.importing_cmd(
            repo_root=repo_root,
            label_storage_file=user_labels.storage_file,
            task_id=subtask_id,
            asset_path=import_dataset_request.asset_dir,
            pred_dir=import_dataset_request.pred_dir,
            gt_dir=import_dataset_request.gt_dir,
            media_location=assets_config['assetskvlocation'],
            work_dir=subtask_workdir,
            unknown_types_strategy=import_dataset_request.unknown_types_strategy,
            object_type=request.object_type,
            anno_fmt=import_dataset_request.anno_format)

        if import_dataset_request.clean_dirs:
            logging.info("trying to clean all data dirs.")
            for d in [import_dataset_request.asset_dir, import_dataset_request.pred_dir, import_dataset_request.gt_dir]:
                try:
                    shutil.rmtree(d)
                except Exception:
                    pass

        return import_dataset_response

    @staticmethod
    def importing_cmd(repo_root: str, label_storage_file: str, task_id: str, asset_path: str, pred_dir: str,
                      gt_dir: str, media_location: str, work_dir: str,
                      unknown_types_strategy: backend_pb2.UnknownTypesStrategy, object_type: mir_cmd_pb.ObjectType,
                      anno_fmt: mir_cmd_pb.AnnoFormat) -> backend_pb2.GeneralResp:
        importing_cmd = [
            utils.mir_executable(), 'import', '--root', repo_root, '--dst-rev', f"{task_id}@{task_id}", '--src-revs',
            'master', '--gen-dir', media_location, '-w', work_dir, "--user-label-file",
            label_storage_file, "--anno-type-fmt",
            f"{utils.object_type_str(object_type)}:{utils.annotation_format_str(anno_fmt)}"
        ]
        if asset_path:
            importing_cmd.extend(['--asset-path', asset_path])
        if pred_dir:
            importing_cmd.extend(['--pred-dir', pred_dir])
        if gt_dir:
            importing_cmd.extend(['--gt-dir', gt_dir])
        importing_cmd.extend([
            '--unknown-types-strategy',
            backend_pb2_utils.unknown_types_strategy_str_from_enum(unknown_types_strategy).value
        ])

        return utils.run_command(importing_cmd, error_code=CMDResponseCode.RC_CMD_INVALID_DATASET)

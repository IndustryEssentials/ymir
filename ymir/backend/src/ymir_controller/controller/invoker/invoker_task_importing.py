import logging
import os
from typing import Dict, List
from common_utils.labels import UserLabels

from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskImportingInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        importing_request = request.req_create_task.importing
        logging.info(f"importing_request: {importing_request}")
        (media_dir, anno_dir, gt_dir) = (importing_request.asset_dir, importing_request.annotation_dir,
                                         importing_request.gt_dir)
        if anno_dir:
            if not os.access(anno_dir, os.R_OK):
                return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                                   message=f"invalid permissions of annotation_dir: {anno_dir}")
        if gt_dir:
            if not os.access(gt_dir, os.R_OK):
                return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                                   message=f"invalid permissions of groundtruth_dir: {gt_dir}")

        if not os.access(media_dir, os.R_OK):
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message=f"invalid permissions of media_dir:{media_dir}")
        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message="")

    @classmethod
    def subtask_weights(cls) -> List[float]:
        return [1.0]

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str, user_labels: UserLabels) -> backend_pb2.GeneralResp:
        importing_request = request.req_create_task.importing

        # Prepare media index-file
        media_dir = importing_request.asset_dir
        media_files = [
            os.path.join(media_dir, f) for f in os.listdir(media_dir) if os.path.isfile(os.path.join(media_dir, f))
        ]
        index_file = os.path.join(subtask_workdir, 'index.txt')
        with open(index_file, 'w') as f:
            f.write('\n'.join(media_files))

        media_location = assets_config['assetskvlocation']
        importing_response = cls.importing_cmd(repo_root=repo_root,
                                               task_id=subtask_id,
                                               index_file=index_file,
                                               annotation_dir=importing_request.annotation_dir,
                                               gt_dir=importing_request.gt_dir,
                                               media_location=media_location,
                                               work_dir=subtask_workdir,
                                               unknown_types_strategy=importing_request.unknown_types_strategy)

        return importing_response

    @staticmethod
    def importing_cmd(repo_root: str, task_id: str, index_file: str, annotation_dir: str, gt_dir: str,
                      media_location: str, work_dir: str,
                      unknown_types_strategy: backend_pb2.UnknownTypesStrategy) -> backend_pb2.GeneralResp:
        importing_cmd = [
            utils.mir_executable(), 'import', '--root', repo_root, '--dataset-name', task_id, '--dst-rev',
            f"{task_id}@{task_id}", '--src-revs', 'master', '--index-file', index_file, '--gt-index-file', index_file,
            '--gen-dir', media_location, '-w', work_dir
        ]
        if annotation_dir:
            importing_cmd.extend(['--annotation-dir', annotation_dir])
        if gt_dir:
            importing_cmd.extend(['--gt-dir', gt_dir])
        importing_cmd.extend(
            ['--unknown-types-strategy',
             TaskImportingInvoker._strategy_str_from_enum(unknown_types_strategy)])

        return utils.run_command(importing_cmd)

    @staticmethod
    def _strategy_str_from_enum(unknown_types_strategy: backend_pb2.UnknownTypesStrategy) -> str:
        mapping = {
            backend_pb2.UnknownTypesStrategy.UTS_STOP: 'stop',
            backend_pb2.UnknownTypesStrategy.UTS_IGNORE: 'ignore',
            backend_pb2.UnknownTypesStrategy.UTS_ADD: 'add'
        }
        return mapping[unknown_types_strategy]

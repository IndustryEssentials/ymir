import argparse
import logging
import os
import shutil

import yaml

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, mir_storage_ops, revs_parser
from mir.tools import settings as mir_settings, utils as mir_utils
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.errors import MirRuntimeError


class CmdModelImport(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command import-model: %s", self.args)

        return CmdModelImport.run_with_args(mir_root=self.args.mir_root,
                                            dst_rev=self.args.dst_rev,
                                            src_revs='master',
                                            work_dir=self.args.work_dir,
                                            package_path=self.args.package_path,
                                            model_location=self.args.model_location)

    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str, dst_rev: str, src_revs: str, work_dir: str, package_path: str,
                      model_location: str) -> int:
        # check args
        if not model_location:
            logging.error('empty --model-location')
            return MirCode.RC_CMD_INVALID_ARGS

        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)

        check_code = checker.check(mir_root,
                                   [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.HAVE_LABELS])
        if check_code != MirCode.RC_OK:
            return check_code

        if not package_path or not os.path.isfile(package_path):
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"model package: {package_path} is not file")

        # unpack
        extract_model_dir_path = os.path.join(work_dir, 'model')
        model_storage = mir_utils.prepare_model(model_location=os.path.dirname(package_path),
                                                model_hash=os.path.basename(package_path),
                                                dst_model_path=extract_model_dir_path)

        logging.info(f"importing model with storage: {model_storage}")

        # check
        _check_model(model_storage=model_storage, mir_root=mir_root)

        # update model_storage and pack
        model_storage.task_context['src-revs'] = src_revs
        model_storage.task_context['dst_rev'] = dst_rev
        model_storage.task_context['type'] = mirpb.TaskType.TaskTypeImportModel
        model_hash = mir_utils.pack_and_copy_models(model_storage=model_storage,
                                                    model_dir_path=extract_model_dir_path,
                                                    model_location=model_location)

        # remove tmp files
        shutil.rmtree(extract_model_dir_path)

        # create task and commit
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeImportModel,
                                           task_id=dst_typ_rev_tid.tid,
                                           message=f"import model {package_path} as {model_hash}",
                                           model_hash=model_hash,
                                           model_mAP=float(model_storage.task_context.get('mAP', 0)),
                                           return_code=MirCode.RC_OK,
                                           return_msg='',
                                           src_revs=src_revs,
                                           dst_rev=dst_rev,
                                           serialized_executor_config=yaml.safe_dump(model_storage.executor_config),
                                           serialized_task_parameters=model_storage.task_context.get(
                                               mir_settings.TASK_CONTEXT_PARAMETERS_KEY, ''),
                                           executor=model_storage.task_context.get('executor', ''))
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_typ_rev_tid.rev,
                                                      his_branch=src_typ_rev_tid.rev,
                                                      mir_datas={},
                                                      task=task)

        return MirCode.RC_OK


def _check_model(model_storage: mir_utils.ModelStorage, mir_root: str) -> int:
    # check producer
    producer = model_storage.task_context.get(mir_settings.PRODUCER_KEY, None)
    if producer != mir_settings.PRODUCER_NAME:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE,
                              error_message=f"can not import model, invalid producer: {producer}")

    return MirCode.RC_OK


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    importing_arg_parser = subparsers.add_parser("models",
                                                 parents=[parent_parser],
                                                 description="use this command to import model package",
                                                 help="import model")
    importing_arg_parser.add_argument("--package-path",
                                      dest="package_path",
                                      type=str,
                                      required=True,
                                      help="path to model package file")
    importing_arg_parser.add_argument("--dst-rev",
                                      dest="dst_rev",
                                      type=str,
                                      required=True,
                                      help="rev@tid: destination branch name and task id")
    importing_arg_parser.add_argument("--model-location",
                                      dest="model_location",
                                      type=str,
                                      required=True,
                                      help="storage place (upload location) to store packed model")
    importing_arg_parser.add_argument('-w', dest='work_dir', type=str, required=True, help='working directory')
    importing_arg_parser.set_defaults(func=CmdModelImport)

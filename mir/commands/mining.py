import argparse
import logging
import os
import time
from typing import Optional
import yaml

from mir.commands import base, infer
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, data_exporter, mir_storage, mir_storage_ops, revs_parser
from mir.tools.code import MirCode


class CmdMining(base.BaseCommand):
    """
    mining command

    About path mappings:
        a. work_dir/in/candidate or cache -> /in/candidate
        b: work_dir/in/model -> /in/model
        c: work_dir/out -> out
        d: work_dir/in/candidate/index.tsv -> /in/candidate/index.tsv
        e: work_dir/in/config.yaml -> /in/config.yaml
    """
    def run(self) -> int:
        logging.debug("command mine: %s", self.args)

        return CmdMining.run_with_args(work_dir=self.args.work_dir,
                                       media_cache=self.args.media_cache,
                                       src_revs=self.args.src_revs,
                                       dst_rev=self.args.dst_rev,
                                       mir_root=self.args.mir_root,
                                       model_hash=self.args.model_hash,
                                       model_location=self.args.model_location,
                                       media_location=self.args.media_location,
                                       config_file=self.args.config_file,
                                       topk=self.args.topk,
                                       executor=self.args.executor,
                                       executor_name=self.args.executor_name)

    @staticmethod
    def run_with_args(work_dir: str,
                      media_cache: Optional[str],
                      src_revs: str,
                      dst_rev: str,
                      mir_root: str,
                      model_hash: str,
                      media_location: str,
                      model_location: str,
                      config_file: str,
                      executor: str,
                      executor_name: str,
                      topk: int = 0) -> int:
        """
        runs a mining task \n
        Args:
            work_dir: mining docker container's work directory
            media_cache: media cache directory
            src_revs: data branch name and base task id
            dst_rev: destination branch name and task id
            mir_root: mir repo path, in order to run in non-mir folder.
            model_hash: used to target model, use prep_tid if non-set
            media_location, model_location: location of assets.
            config_file: path to the config file
            executor: executor name, currently, the docker image name
            executor_name: docker container name
            topk: top k assets you want to save in the result workspace, set to 0 if you want to save all
        Returns:
            error code
        """
        if not mir_root:
            mir_root = '.'
        if not work_dir:
            logging.error("empty work_dir: abort")
            return MirCode.RC_CMD_INVALID_ARGS
        if not media_location or not model_location:
            logging.error("media or model location cannot be none!")
            return MirCode.RC_CMD_INVALID_ARGS
        if not model_hash:
            logging.error("model_hash is required.")
            return MirCode.RC_CMD_INVALID_ARGS

        if not src_revs or not dst_rev:
            logging.error("invalid --src-revs or --dst-rev; abort")
            return MirCode.RC_CMD_INVALID_ARGS
        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs)
        if checker.check_src_revs(src_typ_rev_tid) != MirCode.RC_OK:
            return MirCode.RC_CMD_INVALID_ARGS
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev)
        if checker.check_dst_rev(dst_typ_rev_tid) != MirCode.RC_OK:
            return MirCode.RC_CMD_INVALID_ARGS

        if not config_file:
            logging.warning('empty --config-file, abort')
            return MirCode.RC_CMD_INVALID_ARGS
        if not os.path.isfile(config_file):
            logging.error(f"invalid --config-file {config_file}, not a file, abort")
            return MirCode.RC_CMD_INVALID_ARGS

        if not executor:
            logging.error('empty --executor, abort')
            return MirCode.RC_CMD_INVALID_ARGS

        return_code = checker.check(mir_root, [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            return return_code

        work_in_path = os.path.join(work_dir, "in")  # docker container's input data directory
        work_out_path = os.path.join(work_dir, "out")  # docker container's output data directory
        work_asset_path = media_cache or os.path.join(work_in_path, 'candidate')
        work_model_path = os.path.join(work_in_path, 'model')
        work_index_file = os.path.join(work_in_path, 'candidate', 'src-index.tsv')

        ret = _prepare_env(export_root=work_dir,
                           work_in_path=work_in_path,
                           work_out_path=work_out_path,
                           work_asset_path=work_asset_path,
                           work_model_path=work_model_path)
        if ret != MirCode.RC_OK:
            logging.error("mining enviroment prepare error!")
            return ret

        _prepare_assets(mir_root=mir_root,
                        base_branch=src_typ_rev_tid.rev,
                        media_location=media_location,
                        path_prefix_in_index_file=work_asset_path,
                        work_asset_path=work_asset_path,
                        work_index_file=work_index_file)

        infer.CmdInfer.run_with_args(work_dir=work_dir,
                                     media_path=work_asset_path,
                                     model_location=model_location,
                                     model_hash=model_hash,
                                     index_file=work_index_file,
                                     config_file=config_file,
                                     task_id=dst_typ_rev_tid.tid,
                                     shm_size=_get_shm_size(config_file),
                                     executor=executor,
                                     executor_name=executor_name,
                                     process_infer_results=False)

        _process_mining_results(mir_root=mir_root,
                                export_out=work_out_path,
                                dst_typ_rev_tid=dst_typ_rev_tid,
                                src_typ_rev_tid=src_typ_rev_tid,
                                model_hash=model_hash,
                                topk=topk)
        logging.info(f"mining done, results at: {work_out_path}")

        return MirCode.RC_OK


def _process_mining_results(mir_root: str, export_out: str, dst_typ_rev_tid: revs_parser.TypRevTid,
                            src_typ_rev_tid: revs_parser.TypRevTid, model_hash: str, topk: int) -> int:
    # step 1: build topk results:
    if topk < 0:
        raise RuntimeError("topk cannot be negative")
    topk_result_tsv = os.path.join(export_out, 'result.tsv')
    if not os.path.isfile(topk_result_tsv):
        raise RuntimeError("Cannot find result file {}".format(topk_result_tsv))
    idx_cnt, ret_asset_set = 0, set()
    with open(topk_result_tsv) as ret_f:
        for line in ret_f:
            line = line.strip()
            if not line:
                continue
            if topk > 0 and idx_cnt >= topk:
                break
            ret_asset_set.add(os.path.splitext(os.path.basename(line.split('\t')[0]))[0])
            idx_cnt += 1
    logging.info("top {} samples found".format(len(ret_asset_set)))

    # step 2: update mir data files
    mir_datas = mir_storage_ops.MirStorageOps.load(mir_root=mir_root,
                                                   mir_branch=src_typ_rev_tid.rev,
                                                   mir_storages=mir_storage.get_all_mir_storage())
    mir_metadatas: mirpb.MirMetadatas = mir_datas[mirpb.MirStorage.MIR_METADATAS]
    mir_annotations: mirpb.MirAnnotations = mir_datas[mirpb.MirStorage.MIR_ANNOTATIONS]
    mir_keywords: mirpb.MirKeywords = mir_datas[mirpb.MirStorage.MIR_KEYWORDS]
    mir_tasks: mirpb.MirTasks = mir_datas[mirpb.MirStorage.MIR_TASKS]

    # update mir metadatas
    matched_mir_metadatas = mirpb.MirMetadatas()
    for asset_id in ret_asset_set:
        matched_mir_metadatas.attributes[asset_id].CopyFrom(mir_metadatas.attributes[asset_id])
    logging.info("matched: %d, overriding metadatas.mir", len(matched_mir_metadatas.attributes))

    # update mir annotations
    task_annotation = mir_annotations.task_annotations[mir_annotations.head_task_id]
    joint_asset_ids_set = set(task_annotation.image_annotations.keys()) & ret_asset_set
    matched_mir_annotations = mirpb.MirAnnotations()
    matched_task_annotation = matched_mir_annotations.task_annotations[dst_typ_rev_tid.tid]
    for asset_id in joint_asset_ids_set:
        matched_task_annotation.image_annotations[asset_id].CopyFrom(task_annotation.image_annotations[asset_id])

    # update mir keywords
    joint_asset_ids_set = set(mir_keywords.keywords.keys()) & ret_asset_set
    matched_mir_keywords = mirpb.MirKeywords()
    for asset_id in joint_asset_ids_set:
        matched_mir_keywords.keywords[asset_id].CopyFrom(mir_keywords.keywords[asset_id])

    # update_mir_task
    task = mirpb.Task()
    task.type = mirpb.TaskTypeMining
    task.name = "mining"
    task.task_id = dst_typ_rev_tid.tid
    task.timestamp = int(time.time())
    task.model.model_hash = model_hash
    mir_storage_ops.add_mir_task(mir_tasks, task)

    # step 3: store results and commit.
    mir_datas = {
        mirpb.MirStorage.MIR_METADATAS: matched_mir_metadatas,
        mirpb.MirStorage.MIR_ANNOTATIONS: matched_mir_annotations,
        mirpb.MirStorage.MIR_KEYWORDS: matched_mir_keywords,
        mirpb.MirStorage.MIR_TASKS: mir_tasks,
    }
    mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                  his_branch=src_typ_rev_tid.rev,
                                                  mir_branch=dst_typ_rev_tid.rev,
                                                  mir_datas=mir_datas,
                                                  commit_message=dst_typ_rev_tid.tid)

    return MirCode.RC_OK


def _prepare_env(export_root: str, work_in_path: str, work_out_path: str, work_asset_path: str,
                 work_model_path: str) -> int:
    os.makedirs(export_root, exist_ok=True)
    os.makedirs(work_in_path, exist_ok=True)
    os.makedirs(work_out_path, exist_ok=True)
    os.makedirs(work_asset_path, exist_ok=True)
    os.makedirs(work_model_path, exist_ok=True)

    return MirCode.RC_OK


def _prepare_assets(mir_root: str, base_branch: str, media_location: str, path_prefix_in_index_file: str,
                    work_asset_path: str, work_index_file: str) -> None:
    metadata: mirpb.MirMetadatas = mir_storage_ops.MirStorageOps.load_single(mir_root=mir_root,
                                                                             mir_branch=base_branch,
                                                                             ms=mirpb.MirStorage.MIR_METADATAS)
    if len(metadata.attributes) == 0:
        raise ValueError("no assets found in metadatas.mir")

    os.makedirs(work_asset_path, exist_ok=True)
    os.makedirs(os.path.dirname(work_index_file), exist_ok=True)

    start_time = time.time()  # for test
    img_list = set(metadata.attributes.keys())
    data_exporter.export(mir_root=mir_root,
                         assets_location=media_location,
                         class_type_ids={},
                         asset_ids=img_list,
                         asset_dir=work_asset_path,
                         annotation_dir='',
                         need_ext=True,
                         need_id_sub_folder=True,
                         base_branch=base_branch,
                         format_type=data_exporter.ExportFormat.EXPORT_FORMAT_NO_ANNOTATION,
                         index_file_path=work_index_file,
                         index_prefix=path_prefix_in_index_file)
    logging.info(f"export data time: {time.time() - start_time}")  # for test


def _get_shm_size(mining_config_file_path: str) -> str:
    with open(mining_config_file_path, 'r') as f:
        mining_config = yaml.safe_load(f.read())
    if 'shm_size' not in mining_config:
        return '16G'
    return mining_config['shm_size']


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:  # pragma: no cover
    mining_arg_parser = subparsers.add_parser("mining",
                                              parents=[parent_parser],
                                              description="use this command to mine in current workspace",
                                              help="mine current workspace")
    mining_arg_parser.add_argument("-w",
                                   required=True,
                                   dest="work_dir",
                                   type=str,
                                   help="work place for mining and monitoring")
    mining_arg_parser.add_argument('--cache',
                                   required=False,
                                   dest='media_cache',
                                   type=str,
                                   help='media cache directory')
    mining_arg_parser.add_argument("--model-location",
                                   required=True,
                                   dest="model_location",
                                   type=str,
                                   help="model storage location for models")
    mining_arg_parser.add_argument("--media-location",
                                   required=True,
                                   dest="media_location",
                                   type=str,
                                   help="media storage location for models")
    mining_arg_parser.add_argument("--topk",
                                   dest="topk",
                                   type=int,
                                   default=0,
                                   help="If set, discard samples out of topk, sorting by scores.")
    mining_arg_parser.add_argument("--model-hash",
                                   dest="model_hash",
                                   type=str,
                                   required=True,
                                   help="model hash to be used")
    mining_arg_parser.add_argument("--src-revs",
                                   dest="src_revs",
                                   type=str,
                                   required=True,
                                   help="rev@bid: source rev and base task id")
    mining_arg_parser.add_argument("--dst-rev",
                                   dest="dst_rev",
                                   type=str,
                                   required=True,
                                   help="rev@tid: destination branch name and task id")
    mining_arg_parser.add_argument("--config-file",
                                   dest="config_file",
                                   type=str,
                                   required=True,
                                   help="path to executor config file")
    mining_arg_parser.add_argument("--executor",
                                   required=True,
                                   dest="executor",
                                   type=str,
                                   help="docker image name for mining")
    mining_arg_parser.add_argument('--executor-name',
                                   required=False,
                                   dest='executor_name',
                                   type=str,
                                   help='docker container name for mining')
    mining_arg_parser.set_defaults(func=CmdMining)

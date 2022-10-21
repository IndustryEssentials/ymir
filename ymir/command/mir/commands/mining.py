import argparse
import json
import logging
import os
from subprocess import CalledProcessError
from typing import Dict, Optional, Set

from google.protobuf import json_format

from mir.commands import base, infer
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import annotations, checker, class_ids, env_config, exporter
from mir.tools import mir_storage_ops, models, revs_parser
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.errors import MirContainerError, MirRuntimeError


class CmdMining(base.BaseCommand):
    """
    mining command

    About path mappings:
        a. work_dir/in/assets or cache -> /in/assets
        b: work_dir/in/models -> /in/models
        c: work_dir/out -> out
        d: work_dir/in/candidate-index.tsv -> /in/candidate-index.tsv
        e: work_dir/in/config.yaml -> /in/config.yaml
    """
    def run(self) -> int:
        logging.debug(f"command mining: {self.args}")

        return CmdMining.run_with_args(work_dir=self.args.work_dir,
                                       asset_cache_dir=self.args.asset_cache_dir,
                                       src_revs=self.args.src_revs,
                                       dst_rev=self.args.dst_rev,
                                       mir_root=self.args.mir_root,
                                       model_hash_stage=self.args.model_hash_stage,
                                       model_location=self.args.model_location,
                                       media_location=self.args.media_location,
                                       config_file=self.args.config_file,
                                       topk=self.args.topk,
                                       add_prediction=self.args.add_prediction,
                                       executor=self.args.executor,
                                       executant_name=self.args.executant_name,
                                       run_as_root=self.args.run_as_root)

    @staticmethod
    @command_run_in_out
    def run_with_args(work_dir: str,
                      asset_cache_dir: Optional[str],
                      src_revs: str,
                      dst_rev: str,
                      mir_root: str,
                      model_hash_stage: str,
                      media_location: str,
                      model_location: str,
                      config_file: str,
                      executor: str,
                      executant_name: str,
                      run_as_root: bool,
                      topk: int = None,
                      add_prediction: bool = False) -> int:
        """
        runs a mining task \n
        Args:
            work_dir: mining docker container's work directory
            asset_cache_dir: media cache directory
            src_revs: data branch name and base task id
            dst_rev: destination branch name and task id
            mir_root: mir repo path, in order to run in non-mir folder.
            model_hash_stage: model_hash@stage_name
            media_location, model_location: location of assets.
            config_file: path to the config file
            executor: executor name, currently, the docker image name
            executant_name: docker container name
            topk: top k assets you want to select in the result workspace, positive integer or None (no mining)
            add_prediction: if true, write new prediction into annotations.mir
        Returns:
            error code
        """
        if not mir_root:
            mir_root = '.'
        if not work_dir:
            logging.error('empty work_dir: abort')
            return MirCode.RC_CMD_INVALID_ARGS
        if not media_location or not model_location:
            logging.error('media or model location cannot be none!')
            return MirCode.RC_CMD_INVALID_ARGS
        if not model_hash_stage:
            logging.error('model_hash_stage is required.')
            return MirCode.RC_CMD_INVALID_ARGS

        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)

        if not config_file:
            logging.warning('empty --task-config-file, abort')
            return MirCode.RC_CMD_INVALID_ARGS
        if not os.path.isfile(config_file):
            logging.error(f"invalid --task-config-file {config_file}, not a file, abort")
            return MirCode.RC_CMD_INVALID_ARGS

        if not executor:
            logging.error('empty --executor, abort')
            return MirCode.RC_CMD_INVALID_ARGS

        return_code = checker.check(mir_root, [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            return return_code

        # check `topk` and `add_annotations`
        mir_metadatas: mirpb.MirMetadatas = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=mir_root,
            mir_branch=src_typ_rev_tid.rev,
            mir_task_id=src_typ_rev_tid.tid,
            ms=mirpb.MirStorage.MIR_METADATAS)
        assets_count = len(mir_metadatas.attributes)
        if assets_count == 0:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_MERGE_ERROR,
                                  error_message='no assets found in metadatas.mir')
        if topk:
            if topk >= assets_count:
                logging.warning(f"topk: {topk} >= assets count: {assets_count}, skip mining")
                topk = None
            elif topk <= 0:
                logging.error(f"invalid --topk: {topk}")
                return MirCode.RC_CMD_INVALID_ARGS
        # topk can be None (means no mining), or in interval (0, assets_count) (means mining and select topk)

        work_in_path = os.path.join(work_dir, 'in')  # docker container's input data directory
        work_asset_path = asset_cache_dir or os.path.join(work_in_path, 'assets')
        work_model_path = os.path.join(work_in_path, 'models')
        work_index_file = os.path.join(work_in_path, 'candidate-src-index.tsv')
        work_out_path = os.path.join(work_dir, 'out')  # docker container's output data directory

        ret = _prepare_env(export_root=work_dir,
                           work_in_path=work_in_path,
                           work_out_path=work_out_path,
                           work_asset_path=work_asset_path,
                           work_model_path=work_model_path)
        if ret != MirCode.RC_OK:
            logging.error('mining enviroment prepare error!')
            return ret

        # export assets.
        # mining export abs assets path, which will be converted in-docker path in infer.py.
        ec = mirpb.ExportConfig(asset_format=mirpb.AssetFormat.AF_RAW,
                                asset_dir=work_asset_path,
                                asset_index_file=work_index_file,
                                media_location=media_location,
                                need_sub_folder=True,
                                anno_format=mirpb.AnnoFormat.AF_NO_ANNOTATION,)
        export_code = exporter.export_mirdatas_to_dir(
            mir_metadatas=mir_metadatas,
            ec=ec,
        )
        if export_code != MirCode.RC_OK:
            return export_code

        model_hash, stage_name = models.parse_model_hash_stage(model_hash_stage)
        model_storage = models.prepare_model(model_location=model_location,
                                             model_hash=model_hash,
                                             stage_name=stage_name,
                                             dst_model_path=work_model_path)

        return_code = MirCode.RC_OK
        return_msg = ''
        try:
            return_code = infer.CmdInfer.run_with_args(work_dir=work_dir,
                                                       mir_root=mir_root,
                                                       media_path=work_asset_path,
                                                       model_storage=model_storage,
                                                       index_file=work_index_file,
                                                       config_file=config_file,
                                                       task_id=dst_typ_rev_tid.tid,
                                                       executor=executor,
                                                       executant_name=executant_name,
                                                       run_as_root=run_as_root,
                                                       run_infer=add_prediction,
                                                       run_mining=(topk is not None))
        except CalledProcessError:
            return_code = MirCode.RC_CMD_CONTAINER_ERROR
            return_msg = env_config.collect_executor_outlog_tail(work_dir=work_dir)
        # catch other exceptions in command_run_in_out

        task = mir_storage_ops.create_task(task_type=mirpb.TaskTypeMining,
                                           task_id=dst_typ_rev_tid.tid,
                                           message=f"mining with model: {model_hash_stage}",
                                           src_revs=src_typ_rev_tid.rev_tid,
                                           dst_rev=dst_typ_rev_tid.rev_tid,
                                           return_code=return_code,
                                           return_msg=return_msg,
                                           executor=executor)
        if return_code != MirCode.RC_OK:
            raise MirContainerError(error_message='mining container error occured', task=task)

        _process_results(mir_root=mir_root,
                         export_out=work_out_path,
                         dst_typ_rev_tid=dst_typ_rev_tid,
                         src_typ_rev_tid=src_typ_rev_tid,
                         topk=topk,
                         add_prediction=add_prediction,
                         model_storage=model_storage,
                         task=task)
        logging.info(f"mining done, results at: {work_out_path}")

        return MirCode.RC_OK


# protected: post process
def _process_results(mir_root: str, export_out: str, dst_typ_rev_tid: revs_parser.TypRevTid,
                     src_typ_rev_tid: revs_parser.TypRevTid, topk: Optional[int], add_prediction: bool,
                     model_storage: models.ModelStorage, task: mirpb.Task) -> int:
    # step 1: build topk results:
    #   read old
    mir_metadatas: mirpb.MirMetadatas
    mir_annotations: mirpb.MirAnnotations

    [mir_metadatas, mir_annotations] = mir_storage_ops.MirStorageOps.load_multiple_storages(
        mir_root=mir_root,
        mir_branch=src_typ_rev_tid.rev,
        mir_task_id=src_typ_rev_tid.tid,
        ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS],
        as_dict=False,
    )

    #   parse new: topk and new annotations (both optional)
    topk_result_file_path = os.path.join(export_out, 'result.tsv')
    asset_ids_set = (_get_topk_asset_ids(file_path=topk_result_file_path, topk=topk)
                     if topk is not None else set(mir_metadatas.attributes.keys()))

    infer_result_file_path = os.path.join(export_out, 'infer-result.json')
    cls_id_mgr = class_ids.load_or_create_userlabels(mir_root=mir_root)
    asset_id_to_annotations = (_get_infer_annotations(
        file_path=infer_result_file_path, asset_ids_set=asset_ids_set, cls_id_mgr=cls_id_mgr) if add_prediction else {})

    # step 2: update mir data files
    #   update mir metadatas
    matched_mir_metadatas = mirpb.MirMetadatas()
    for asset_id in asset_ids_set:
        matched_mir_metadatas.attributes[asset_id].CopyFrom(mir_metadatas.attributes[asset_id])
    logging.info(f"matched: {len(matched_mir_metadatas.attributes)}, overriding metadatas.mir")

    #   update mir annotations: predictions
    matched_mir_annotations = mirpb.MirAnnotations()
    prediction = matched_mir_annotations.prediction
    prediction.type = mirpb.AnnoType.AT_DET_BOX
    if add_prediction:
        # add new
        for asset_id, single_image_annotations in asset_id_to_annotations.items():
            prediction.image_annotations[asset_id].CopyFrom(single_image_annotations)
        prediction.eval_class_ids[:] = set(
            cls_id_mgr.id_for_names(model_storage.class_names, drop_unknown_names=True)[0])
        prediction.executor_config = json.dumps(model_storage.executor_config)
        prediction.model.CopyFrom(model_storage.get_model_meta())
    else:
        # use old
        pred_asset_ids = set(mir_annotations.prediction.image_annotations.keys()) & asset_ids_set
        for asset_id in pred_asset_ids:
            prediction.image_annotations[asset_id].CopyFrom(mir_annotations.prediction.image_annotations[asset_id])
        annotations.copy_annotations_pred_meta(src_task_annotations=mir_annotations.prediction,
                                               dst_task_annotations=prediction)

    #   update mir annotations: ground truth
    ground_truth = matched_mir_annotations.ground_truth
    gt_asset_ids = set(mir_annotations.ground_truth.image_annotations.keys()) & asset_ids_set
    for asset_id in gt_asset_ids:
        ground_truth.image_annotations[asset_id].CopyFrom(mir_annotations.ground_truth.image_annotations[asset_id])

    image_ck_asset_ids = set(mir_annotations.image_cks.keys() & asset_ids_set)
    for asset_id in image_ck_asset_ids:
        matched_mir_annotations.image_cks[asset_id].CopyFrom(mir_annotations.image_cks[asset_id])

    # step 3: store results and commit.
    mir_datas = {
        mirpb.MirStorage.MIR_METADATAS: matched_mir_metadatas,
        mirpb.MirStorage.MIR_ANNOTATIONS: matched_mir_annotations,
    }
    mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                  his_branch=src_typ_rev_tid.rev,
                                                  mir_branch=dst_typ_rev_tid.rev,
                                                  mir_datas=mir_datas,
                                                  task=task)

    return MirCode.RC_OK


def _get_topk_asset_ids(file_path: str, topk: int) -> Set[str]:
    if not os.path.isfile(file_path):
        raise MirRuntimeError(MirCode.RC_CMD_NO_RESULT, f"Cannot find result file {file_path}")

    asset_ids_set: Set[str] = set()
    idx_cnt = 0
    with open(file_path) as ret_f:
        for line in ret_f:
            line = line.strip()
            if not line:
                continue
            if idx_cnt >= topk:
                break
            asset_ids_set.add(os.path.splitext(os.path.basename(line.split('\t')[0]))[0])  # main file name (asset id)
            idx_cnt += 1
    logging.info(f"top {len(asset_ids_set)} samples found")
    return asset_ids_set


def _get_infer_annotations(file_path: str, asset_ids_set: Set[str],
                           cls_id_mgr: class_ids.UserLabels) -> Dict[str, mirpb.SingleImageAnnotations]:
    asset_id_to_annotations: dict = {}
    with open(file_path, 'r') as f:
        results = json.loads(f.read())

    detections = results.get('detection')
    if not isinstance(detections, dict):
        logging.error('invalid infer-result.json')
        return asset_id_to_annotations

    for asset_name, annotations_dict in detections.items():
        annotations = annotations_dict.get('boxes')
        if not isinstance(annotations, list):
            logging.error(f"invalid annotations: {annotations}")
            continue

        asset_id = os.path.splitext(os.path.basename(asset_name))[0]
        if asset_id not in asset_ids_set:
            continue

        single_image_annotations = mirpb.SingleImageAnnotations()
        idx = 0
        for annotation_dict in annotations:
            class_id = cls_id_mgr.id_and_main_name_for_name(name=annotation_dict['class_name'])[0]
            # ignore unknown class ids
            if class_id < 0:
                continue

            annotation = mirpb.ObjectAnnotation()
            annotation.index = idx
            json_format.ParseDict(annotation_dict['box'], annotation.box)
            annotation.class_id = class_id
            annotation.score = float(annotation_dict.get('score', 0))
            single_image_annotations.boxes.append(annotation)
            idx += 1
        asset_id_to_annotations[asset_id] = single_image_annotations
    return asset_id_to_annotations


# protected: pre process
def _prepare_env(export_root: str, work_in_path: str, work_out_path: str, work_asset_path: str,
                 work_model_path: str) -> int:
    os.makedirs(export_root, exist_ok=True)
    os.makedirs(work_in_path, exist_ok=True)
    os.makedirs(work_out_path, exist_ok=True)
    os.makedirs(work_asset_path, exist_ok=True)
    os.makedirs(work_model_path, exist_ok=True)

    return MirCode.RC_OK


# public: arg parser
def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    mining_arg_parser = subparsers.add_parser('mining',
                                              parents=[parent_parser],
                                              description='use this command to mine in current workspace',
                                              help='mine current workspace')
    mining_arg_parser.add_argument('-w',
                                   required=True,
                                   dest='work_dir',
                                   type=str,
                                   help='work place for mining and monitoring')
    mining_arg_parser.add_argument('--asset-cache-dir',
                                   required=False,
                                   dest='asset_cache_dir',
                                   type=str,
                                   help='media cache directory')
    mining_arg_parser.add_argument('--model-location',
                                   required=True,
                                   dest='model_location',
                                   type=str,
                                   help='model storage location')
    mining_arg_parser.add_argument('--media-location',
                                   required=True,
                                   dest='media_location',
                                   type=str,
                                   help='media storage location')
    mining_arg_parser.add_argument('--topk',
                                   dest='topk',
                                   type=int,
                                   required=False,
                                   help='if set, discard samples out of topk, sorting by scores.')
    mining_arg_parser.add_argument('--add-prediction',
                                   dest='add_prediction',
                                   action='store_true',
                                   required=False,
                                   help='if set, also add inference result')
    mining_arg_parser.add_argument('--model-hash',
                                   dest='model_hash_stage',
                                   type=str,
                                   required=True,
                                   help='model hash@stage to be used')
    mining_arg_parser.add_argument('--src-revs',
                                   dest='src_revs',
                                   type=str,
                                   required=True,
                                   help='rev@bid: source rev and base task id')
    mining_arg_parser.add_argument('--dst-rev',
                                   dest='dst_rev',
                                   type=str,
                                   required=True,
                                   help='rev@tid: destination branch name and task id')
    mining_arg_parser.add_argument('--task-config-file',
                                   dest='config_file',
                                   type=str,
                                   required=True,
                                   help='path to executor config file')
    mining_arg_parser.add_argument('--executor',
                                   required=True,
                                   dest='executor',
                                   type=str,
                                   help='docker image name for mining')
    mining_arg_parser.add_argument('--executant-name',
                                   required=False,
                                   dest='executant_name',
                                   type=str,
                                   help='docker container name for mining')
    mining_arg_parser.add_argument("--run-as-root",
                                   dest="run_as_root",
                                   action='store_true',
                                   help="run executor as root user")
    mining_arg_parser.set_defaults(func=CmdMining)

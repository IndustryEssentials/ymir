from collections import defaultdict
from functools import reduce
from math import ceil
import os
import time
from typing import Any, List, Dict, Optional, Set

import fasteners  # type: ignore
from google.protobuf import json_format
import yaml

from mir import scm
from mir.commands.checkout import CmdCheckout
from mir.commands.commit import CmdCommit
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import class_ids, context, det_eval_ops, exodus
from mir.tools import mir_storage, mir_repo_utils, revs_parser
from mir.tools import settings as mir_settings
from mir.tools.code import MirCode
from mir.tools.errors import MirError, MirRuntimeError


def create_evaluate_config(conf_thr: float = mir_settings.DEFAULT_EVALUATE_CONF_THR,
                           iou_thrs: str = mir_settings.DEFAULT_EVALUATE_IOU_THR,
                           need_pr_curve: bool = False,
                           class_ids: List[int] = []) -> mirpb.EvaluateConfig:
    evaluate_config = mirpb.EvaluateConfig()
    evaluate_config.conf_thr = conf_thr
    evaluate_config.iou_thrs_interval = iou_thrs
    evaluate_config.need_pr_curve = need_pr_curve
    evaluate_config.class_ids[:] = class_ids
    return evaluate_config


class MirStorageOps():
    # private: save and load
    @classmethod
    def __build_and_save(cls, mir_root: str, mir_datas: Dict['mirpb.MirStorage.V', Any],
                         evaluate_config: mirpb.EvaluateConfig, dst_dataset_id: str) -> None:
        # add default members
        mir_metadatas: mirpb.MirMetadatas = mir_datas[mirpb.MirStorage.MIR_METADATAS]
        mir_tasks: mirpb.MirTasks = mir_datas[mirpb.MirStorage.MIR_TASKS]
        mir_annotations: mirpb.MirAnnotations = mir_datas[mirpb.MirStorage.MIR_ANNOTATIONS]

        cls.__build_annotations_head_task_id(mir_annotations=mir_annotations, head_task_id=mir_tasks.head_task_id)

        # gen mir_keywords
        mir_keywords: mirpb.MirKeywords = mirpb.MirKeywords()
        cls.__build_mir_keywords(mir_metadatas=mir_metadatas,
                                 mir_annotations=mir_annotations,
                                 mir_keywords=mir_keywords)
        mir_datas[mirpb.MirStorage.MIR_KEYWORDS] = mir_keywords

        evaluation = det_eval_ops.det_evaluate_with_pb(
            prediction=mir_annotations.prediction,
            ground_truth=mir_annotations.ground_truth,
            config=evaluate_config,
        )
        mir_tasks.tasks[mir_tasks.head_task_id].evaluation.CopyFrom(evaluation)

        # gen mir_context
        project_class_ids = context.load(mir_root=mir_root)
        mir_context = mirpb.MirContext()
        cls.__build_mir_context(mir_metadatas=mir_datas[mirpb.MirStorage.MIR_METADATAS],
                                mir_annotations=mir_annotations,
                                mir_keywords=mir_keywords,
                                project_class_ids=project_class_ids,
                                mir_context=mir_context)
        mir_datas[mirpb.MirStorage.MIR_CONTEXT] = mir_context

        # save to file
        for ms, mir_data in mir_datas.items():
            mir_file_path = os.path.join(mir_root, mir_storage.mir_path(ms))
            with open(mir_file_path, "wb") as m_f:
                m_f.write(mir_data.SerializeToString())

    # public: presave actions
    @classmethod
    def __build_annotations_head_task_id(cls, mir_annotations: mirpb.MirAnnotations, head_task_id: str) -> None:
        mir_annotations.head_task_id = head_task_id
        mir_annotations.prediction.task_id = head_task_id
        mir_annotations.ground_truth.task_id = head_task_id

    @classmethod
    def __build_mir_keywords(cls, mir_metadatas: mirpb.MirMetadatas, mir_annotations: mirpb.MirAnnotations,
                             mir_keywords: mirpb.MirKeywords) -> None:
        """
        build mir_keywords from mir_annotations

        Args:
            mir_annotations (mirpb.MirAnnotations)
            mir_keywords (mirpb.MirKeywords)
        """

        for asset_id in mir_metadatas.attributes:
            pred_cis_set = set()
            gt_cis_set = set()

            if asset_id in mir_annotations.prediction.image_annotations:
                image_annotation = mir_annotations.prediction.image_annotations[asset_id]
                pred_cis_set.update([annotation.class_id for annotation in image_annotation.annotations])
            if asset_id in mir_annotations.ground_truth.image_annotations:
                image_annotation = mir_annotations.ground_truth.image_annotations[asset_id]
                gt_cis_set.update([annotation.class_id for annotation in image_annotation.annotations])

            if pred_cis_set:
                mir_keywords.keywords[asset_id].predefined_keyids[:] = pred_cis_set
            if gt_cis_set:
                mir_keywords.keywords[asset_id].gt_predefined_keyids[:] = gt_cis_set
        cls.__build_mir_keywords_ci_tag(task_annotations=mir_annotations.prediction,
                                        keyword_to_index=mir_keywords.pred_idx)
        cls.__build_mir_keywords_ci_tag(task_annotations=mir_annotations.ground_truth,
                                        keyword_to_index=mir_keywords.gt_idx)

        # ck to assets
        for asset_id, image_cks in mir_annotations.image_cks.items():
            for k, v in image_cks.cks.items():
                mir_keywords.ck_idx[k].asset_annos[asset_id]  # empty record to asset id
                mir_keywords.ck_idx[k].sub_indexes[v].key_ids[asset_id]  # empty record to asset id

    @classmethod
    def __build_mir_keywords_ci_tag(cls, task_annotations: mirpb.SingleTaskAnnotations,
                                    keyword_to_index: mirpb.KeywordToIndex) -> None:
        for asset_id, single_image_annotations in task_annotations.image_annotations.items():
            for annotation in single_image_annotations.annotations:
                # ci to annos
                keyword_to_index.cis[annotation.class_id].key_ids[asset_id].ids.append(annotation.index)

                # tags to annos
                for k, v in annotation.tags.items():
                    keyword_to_index.tags[k].asset_annos[asset_id].ids.append(annotation.index)
                    keyword_to_index.tags[k].sub_indexes[v].key_ids[asset_id].ids.append(annotation.index)

    @classmethod
    def __build_mir_context_stats(cls, anno_stats: mirpb.AnnoStats, mir_metadatas: mirpb.MirMetadatas,
                                  task_annotations: mirpb.SingleTaskAnnotations,
                                  keyword_to_index: mirpb.KeywordToIndex) -> None:
        image_annotations = task_annotations.image_annotations

        # anno_stats.asset_cnt
        anno_stats.positive_asset_cnt = len(image_annotations)
        anno_stats.negative_asset_cnt = len(mir_metadatas.attributes) - len(image_annotations)

        # anno_stats.quality_hist
        all_annotations = [
            annotation for image_annotation in image_annotations.values() for annotation in image_annotation.annotations
        ]
        anno_stats.total_cnt = len(all_annotations)
        anno_quality_hist: Dict[float, int] = cls.__build_hist(
            values=[annotation.anno_quality for annotation in all_annotations],
            desc_lower_bnds=mir_settings.QUALITY_DESC_LOWER_BNDS)
        anno_stats.quality_hist.update({f"{k:.2f}": v for k, v in anno_quality_hist.items()})

        # anno_stats.area_hist
        anno_area_hist: Dict[int, int] = cls.__build_hist(
            values=[annotation.box.w * annotation.box.h for annotation in all_annotations],
            desc_lower_bnds=mir_settings.ANNO_AREA_DESC_LOWER_BNDS)
        anno_stats.area_hist.update(anno_area_hist)

        # anno_stats.area_ratio_hist
        all_area_ratios = []
        for asset_id, image_annotation in image_annotations.items():
            attrs = mir_metadatas.attributes[asset_id]
            asset_area = attrs.width * attrs.height
            for annotation in image_annotation.annotations:
                all_area_ratios.append(annotation.box.w * annotation.box.h / asset_area if asset_area else -1)
        anno_area_ratio_hist = cls.__build_hist(values=all_area_ratios,
                                                desc_lower_bnds=mir_settings.QUALITY_DESC_LOWER_BNDS)
        anno_stats.area_ratio_hist.update({f"{k:.2f}": v for k, v in anno_area_ratio_hist.items()})

        # anno_stats.cis_cnt
        for ci, ci_assets in keyword_to_index.cis.items():
            anno_stats.class_ids_cnt[ci] = len(ci_assets.key_ids)

        # anno_stats.tags_cnt
        for tag, tag_to_annos in keyword_to_index.tags.items():
            for anno_idxes in tag_to_annos.asset_annos.values():
                anno_stats.tags_cnt[tag].cnt += len(anno_idxes.ids)

            for sub_tag, sub_tag_to_annos in tag_to_annos.sub_indexes.items():
                for anno_idxes in sub_tag_to_annos.key_ids.values():
                    anno_stats.tags_cnt[tag].sub_cnt[sub_tag] += len(anno_idxes.ids)

    @classmethod
    def __build_mir_context(cls, mir_metadatas: mirpb.MirMetadatas, mir_annotations: mirpb.MirAnnotations,
                            mir_keywords: mirpb.MirKeywords, project_class_ids: List[int],
                            mir_context: mirpb.MirContext) -> None:
        # ci to asset count
        ci_to_asset_ids: Dict[int, Set[str]] = defaultdict(set)
        for ci, ci_assets in mir_keywords.gt_idx.cis.items():
            ci_to_asset_ids[ci].update(ci_assets.key_ids.keys())
        for ci, ci_assets in mir_keywords.pred_idx.cis.items():
            ci_to_asset_ids[ci].update(ci_assets.key_ids.keys())
        for ci, asset_ids_set in ci_to_asset_ids.items():
            mir_context.predefined_keyids_cnt[ci] = len(asset_ids_set)

        # project_predefined_keyids_cnt: assets count for project class ids
        #   suppose we have: 13 images for key 5, 15 images for key 6, and proejct_class_ids = [3, 5]
        #   project_predefined_keyids_cnt should be: {3: 0, 5: 13}
        project_positive_asset_ids: Set[str] = set()
        for key_id in project_class_ids:
            if key_id in mir_context.predefined_keyids_cnt:
                mir_context.project_predefined_keyids_cnt[key_id] = mir_context.predefined_keyids_cnt[key_id]
                project_positive_asset_ids.update([x for x in mir_keywords.pred_idx.cis[key_id].key_ids])
            else:
                mir_context.project_predefined_keyids_cnt[key_id] = 0

        # image_cnt, negative_images_cnt, project_negative_images_cnt
        mir_context.images_cnt = len(mir_metadatas.attributes)
        mir_context.negative_images_cnt = mir_context.images_cnt - len(mir_annotations.prediction.image_annotations)
        if project_class_ids:
            mir_context.project_negative_images_cnt = mir_context.images_cnt - len(project_positive_asset_ids)
            # if no project_class_ids, project_negative_images_cnt set to 0

        total_asset_bytes = reduce(lambda s, v: s + v.byte_size, mir_metadatas.attributes.values(), 0)
        mir_context.total_asset_mbytes = ceil(total_asset_bytes / mir_settings.BYTES_PER_MB)

        # cks cnt
        for ck, ck_assets in mir_keywords.ck_idx.items():
            mir_context.cks_cnt[ck].cnt = len(ck_assets.asset_annos)
            for sub_ck, sub_ck_to_assets in ck_assets.sub_indexes.items():
                mir_context.cks_cnt[ck].sub_cnt[sub_ck] = len(sub_ck_to_assets.key_ids)

        # asset_quality_hist
        asset_quality_hist = cls.__build_hist(values=[x.image_quality for x in mir_annotations.image_cks.values()],
                                              desc_lower_bnds=mir_settings.QUALITY_DESC_LOWER_BNDS)
        mir_context.asset_quality_hist.update({f"{k:.2f}": v for k, v in asset_quality_hist.items()})

        # asset bytes hist
        asset_bytes_hist = cls.__build_hist(values=[x.byte_size for x in mir_metadatas.attributes.values()],
                                            desc_lower_bnds=mir_settings.ASSET_BYTES_DESC_LOWER_BNDS)
        mir_context.asset_bytes_hist.update(
            {f"{k/mir_settings.BYTES_PER_MB:.1f}MB": v
             for k, v in asset_bytes_hist.items()})

        # asset area hist
        asset_area_hist = cls.__build_hist(values=[x.width * x.height for x in mir_metadatas.attributes.values()],
                                           desc_lower_bnds=mir_settings.ASSET_AREA_DESC_LOWER_BNDS)
        mir_context.asset_area_hist.update(asset_area_hist)

        # asset hw ratio hist
        asset_hw_ratio_hist = cls.__build_hist(values=[x.height / x.width for x in mir_metadatas.attributes.values()],
                                               desc_lower_bnds=mir_settings.ASSET_HW_RATIO_DESC_LOWER_BNDS)
        mir_context.asset_hw_ratio_hist.update({f"{k:.2f}": v for k, v in asset_hw_ratio_hist.items()})

        # pred_stats
        cls.__build_mir_context_stats(anno_stats=mir_context.pred_stats,
                                      mir_metadatas=mir_metadatas,
                                      task_annotations=mir_annotations.prediction,
                                      keyword_to_index=mir_keywords.pred_idx)
        cls.__build_mir_context_stats(anno_stats=mir_context.gt_stats,
                                      mir_metadatas=mir_metadatas,
                                      task_annotations=mir_annotations.ground_truth,
                                      keyword_to_index=mir_keywords.gt_idx)

    @classmethod
    def __build_hist(cls, values: List[Any], desc_lower_bnds: List[Any]) -> Dict[Any, int]:
        hist = {}
        if not desc_lower_bnds:
            raise ValueError('empty desc_lower_bnds')
        for x in desc_lower_bnds:
            hist[x] = 0
        for y in values:
            for x in desc_lower_bnds:
                if y >= x:
                    hist[x] += 1
                    break
        return hist

    @classmethod
    def __add_git_tag(cls, mir_root: str, tag: str) -> None:
        repo_git = scm.Scm(root_dir=mir_root, scm_executable='git')
        repo_git.tag(tag)

    # public: save and load
    @classmethod
    def save_and_commit(cls,
                        mir_root: str,
                        mir_branch: str,
                        his_branch: Optional[str],
                        mir_datas: Dict,
                        task: mirpb.Task,
                        evaluate_config: Optional[mirpb.EvaluateConfig] = None) -> int:
        """
        saves and commit all contents in mir_datas to branch: `mir_branch`;
        branch will be created if not exists, and it's history will be after `his_branch`

        Args:
            mir_root (str): path to mir repo
            mir_branch (str): branch you wish to save to, if not exists, create new one
            his_branch (Optional[str]): if `mir_branch` not exists, this is the branch where you wish to start with
            mir_datas (Dict[mirpb.MirStorage.V, pb_message.Message]): datas you wish to save, need no mir_keywords,
                mir_tasks is needed, if mir_metadatas and mir_annotations not provided, they will be created as empty
                 datasets
            task (mirpb.Task): task for this commit
            evaluate_config (mirpb.EvaluateConfig): evaluate config

        Raises:
            MirRuntimeError

        Returns:
            int: result code
        """
        if not mir_root:
            mir_root = '.'
        if not mir_branch:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="empty mir branch")
        if mirpb.MirStorage.MIR_METADATAS not in mir_datas or mirpb.MirStorage.MIR_ANNOTATIONS not in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='need mir_metadatas and mir_annotations')
        if mirpb.MirStorage.MIR_KEYWORDS in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='need no mir_keywords')
        if mirpb.MirStorage.MIR_CONTEXT in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='need no mir_context')
        if mirpb.MirStorage.MIR_TASKS in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='need no mir_tasks')
        if not task.name:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="empty commit message")
        if not task.task_id:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty task id')

        if not evaluate_config:
            evaluate_config = create_evaluate_config()

        mir_tasks: mirpb.MirTasks = mirpb.MirTasks()
        mir_tasks.head_task_id = task.task_id
        mir_tasks.tasks[mir_tasks.head_task_id].CopyFrom(task)
        mir_datas[mirpb.MirStorage.MIR_TASKS] = mir_tasks

        branch_exists = mir_repo_utils.mir_check_branch_exists(mir_root=mir_root, branch=mir_branch)
        if not branch_exists and not his_branch:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_BRANCH_OR_TAG,
                                  error_message=f"branch {mir_branch} not exists, and his_branch not provided")

        # checkout to proper branch
        # if mir_branch exists, checkout mir_branch
        # if not exists, checkout his_branch, and checkout -b mir_branch
        if branch_exists:
            his_branch = mir_branch

        lock = fasteners.InterProcessLock(os.path.join(mir_root, '.mir_lock'))
        with lock:
            # checkout to his branch
            # cmd checkout also checks whether current branch is clean
            return_code = CmdCheckout.run_with_args(mir_root=mir_root, commit_id=str(his_branch), branch_new=False)
            if return_code != MirCode.RC_OK:
                return return_code

            # create dest_branch if not exists
            if not branch_exists:
                return_code = CmdCheckout.run_with_args(mir_root=mir_root, commit_id=mir_branch, branch_new=True)
                if return_code != MirCode.RC_OK:
                    return return_code

            cls.__build_and_save(mir_root=mir_root, mir_datas=mir_datas, evaluate_config=evaluate_config,
                                 dst_dataset_id=revs_parser.join_rev_tid(mir_branch, task.task_id))

            ret_code = CmdCommit.run_with_args(mir_root=mir_root, msg=task.name)
            if ret_code != MirCode.RC_OK:
                return ret_code

            # also have a tag for this commit
            cls.__add_git_tag(mir_root=mir_root, tag=revs_parser.join_rev_tid(mir_branch, task.task_id))

        return ret_code

    # public: load
    @classmethod
    def load_single_storage(cls,
                            mir_root: str,
                            mir_branch: str,
                            ms: 'mirpb.MirStorage.V',
                            mir_task_id: str = '',
                            as_dict: bool = False) -> Any:
        rev = revs_parser.join_rev_tid(mir_branch, mir_task_id)

        mir_pb_type = mir_storage.mir_type(ms)
        mir_storage_data = mir_pb_type()
        mir_storage_data.ParseFromString(exodus.read_mir(mir_root=mir_root, rev=rev,
                                                         file_name=mir_storage.mir_path(ms)))

        if as_dict:
            mir_storage_data = cls.__message_to_dict(mir_storage_data)

        return mir_storage_data

    @classmethod
    def load_multiple_storages(cls,
                               mir_root: str,
                               mir_branch: str,
                               ms_list: List['mirpb.MirStorage.V'],
                               mir_task_id: str = '',
                               as_dict: bool = False) -> List[Any]:
        return [
            cls.load_single_storage(
                mir_root=mir_root,
                mir_branch=mir_branch,
                ms=ms,
                mir_task_id=mir_task_id,
                as_dict=as_dict,
            ) for ms in ms_list
        ]

    @classmethod
    def __message_to_dict(cls, message: Any) -> Dict:
        return json_format.MessageToDict(message,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True,
                                         including_default_value_fields=True)

    @classmethod
    def load_single_model(cls, mir_root: str, mir_branch: str, mir_task_id: str = '') -> Dict:
        mir_storage_data: mirpb.MirTasks = cls.load_single_storage(mir_root=mir_root,
                                                                   mir_branch=mir_branch,
                                                                   ms=mirpb.MirStorage.MIR_TASKS,
                                                                   mir_task_id=mir_task_id,
                                                                   as_dict=False)
        task = mir_storage_data.tasks[mir_storage_data.head_task_id]
        if not task.model.model_hash:
            raise MirError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="no model")

        single_model_dict = cls.__message_to_dict(task.model)
        single_model_dict[mir_settings.TASK_CONTEXT_PARAMETERS_KEY] = task.serialized_task_parameters
        single_model_dict[mir_settings.EXECUTOR_CONFIG_KEY] = yaml.safe_load(task.serialized_executor_config) or {}
        return single_model_dict

    @classmethod
    def load_single_dataset(cls, mir_root: str, mir_branch: str, mir_task_id: str = '') -> Dict:
        """
        exampled return data:
        {
            "total_assets_mbytes":222,
            "total_assets_count":1420,
            "new_types_added":False,
            "cks_count_total":{},
            "cks_count":{},
            "hist":{
                "asset_quality": [],
                "asset_bytes": [],
                "asset_area": [],
                "asset_hw_ratio": [],
            },
            "pred":{
                "class_ids_count":{},
                "negative_assets_count":14,
                "tags_count_total":{},
                "tags_count":{},
                "hist":{
                    "anno_quality":[],
                    "anno_area":[],
                    "anno_area_ratio":[]
                },
                "annos_count":10006,
            },
            "gt":{}
        }
        """
        mir_storage_tasks: mirpb.MirTasks
        mir_storage_context: mirpb.MirContext

        mir_storage_tasks, mir_storage_context = cls.load_multiple_storages(
            mir_root=mir_root,
            mir_branch=mir_branch,
            ms_list=[mirpb.MirStorage.MIR_TASKS, mirpb.MirStorage.MIR_CONTEXT],
            mir_task_id=mir_task_id,
            as_dict=False,
        )
        task_storage = mir_storage_tasks.tasks[mir_storage_tasks.head_task_id]

        class_id_mgr = class_ids.ClassIdManager(mir_root=mir_root)
        result = dict(
            total_assets_mbytes=mir_storage_context.total_asset_mbytes,
            total_assets_count=mir_storage_context.images_cnt,
            hist=dict(
                asset_quality=cls._gen_viz_hist(mir_storage_context.asset_quality_hist),
                asset_bytes=cls._gen_viz_hist(mir_storage_context.asset_bytes_hist),
                asset_area=cls._gen_viz_hist(mir_storage_context.asset_area_hist),
                asset_hw_ratio=cls._gen_viz_hist(mir_storage_context.asset_hw_ratio_hist),
            ),
            new_types_added=task_storage.new_types_added,
            cks_count_total={k: v.cnt
                             for k, v in mir_storage_context.cks_cnt.items()},
            cks_count={k: {k2: v2
                           for k2, v2 in v.sub_cnt.items()}
                       for k, v in mir_storage_context.cks_cnt.items()},
            pred=cls._load_single_dataset_pred_or_gt_info(mir_storage_context=mir_storage_context,
                                                          task_storage=task_storage,
                                                          class_id_mgr=class_id_mgr,
                                                          is_gt=False),
            gt=cls._load_single_dataset_pred_or_gt_info(mir_storage_context=mir_storage_context,
                                                        task_storage=task_storage,
                                                        class_id_mgr=class_id_mgr,
                                                        is_gt=True),
        )
        return result

    @classmethod
    def load_assets_content(cls, mir_root: str, mir_branch: str, mir_task_id: str = '') -> Dict:
        """
        exampled return data:
        {
            "all_asset_ids": ["asset_id"],
            "asset_ids_detail": {
                "asset_id": {
                    "metadata": {"asset_type": 2, "width": 1080, "height": 1620},
                    "annotations": [{"box": {"x": 26, "y": 189, "w": 19, "h": 50}, "class_id": 2}],
                    "class_ids": [2],
                }
            },
            "class_ids_index": {2: ["asset_id"]},
        }
        """
        # Require asset details, build snapshot.
        mir_storage_metadatas, mir_storage_annotations, mir_storage_keywords = cls.load_multiple_storages(
            mir_root=mir_root,
            mir_branch=mir_branch,
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS, mirpb.MirStorage.MIR_KEYWORDS],
            mir_task_id=mir_task_id,
            as_dict=True,
        )

        asset_ids_detail: Dict[str, Dict] = dict()
        pred_annotations = mir_storage_annotations.get('prediction', {}).get('image_annotations', {})
        gt_annotations = mir_storage_annotations.get('ground_truth', {}).get('image_annotations', {})
        keyword_keyids_list = mir_storage_keywords["keywords"]
        for asset_id, asset_metadata in mir_storage_metadatas["attributes"].items():
            pred_asset_annotations = pred_annotations[asset_id]["annotations"] if asset_id in pred_annotations else []
            gt_asset_annotations = gt_annotations[asset_id]["annotations"] if asset_id in gt_annotations else []
            pred_class_ids = (keyword_keyids_list[asset_id]["predefined_keyids"]
                              if asset_id in keyword_keyids_list else [])
            gt_class_ids = (keyword_keyids_list[asset_id]["gt_predefined_keyids"]
                            if asset_id in keyword_keyids_list else [])
            class_ids = list(set(pred_class_ids) | set(gt_class_ids))
            asset_ids_detail[asset_id] = dict(
                metadata=asset_metadata,
                pred=pred_asset_annotations,
                gt=gt_asset_annotations,
                pred_class_ids=pred_class_ids,
                gt_class_ids=gt_class_ids,
                class_ids=class_ids,
            )

        class_id_to_assets: Dict[int, Set[str]] = defaultdict(set)  # total
        for k, v in mir_storage_keywords.get('pred_idx', {}).get('cis', {}).items():
            class_id_to_assets[k].update(v.get('key_ids', {}))
        for k, v in mir_storage_keywords.get('gt_idx', {}).get('cis', {}).items():
            class_id_to_assets[k].update(v.get('key_ids', {}))

        return dict(
            all_asset_ids=sorted([*mir_storage_metadatas["attributes"].keys()]),  # ordered list.
            asset_ids_detail=asset_ids_detail,
            class_ids_index={k: list(v)
                             for k, v in class_id_to_assets.items()},
            pred_class_ids_index={
                k: v.get('key_ids')
                for k, v in mir_storage_keywords.get('pred_idx', {}).get('cis', {}).items()
            },
            gt_class_ids_index={
                k: v.get('key_ids')
                for k, v in mir_storage_keywords.get('gt_idx', {}).get('cis', {}).items()
            },
        )

    @classmethod
    def load_dataset_evaluation(cls, mir_root: str, mir_branch: str, mir_task_id: str = '') -> Dict:
        mir_storage_data: mirpb.MirTasks = cls.load_single_storage(mir_root=mir_root,
                                                                   mir_branch=mir_branch,
                                                                   ms=mirpb.MirStorage.MIR_TASKS,
                                                                   mir_task_id=mir_task_id,
                                                                   as_dict=False)
        task = mir_storage_data.tasks[mir_storage_data.head_task_id]
        return cls.__message_to_dict(task.evaluation.dataset_evaluation)

    @classmethod
    def load_dataset_metadata(cls, mir_root: str, mir_branch: str, mir_task_id: str = '') -> Dict:
        mir_storage_data = cls.load_single_storage(mir_root=mir_root,
                                                   mir_branch=mir_branch,
                                                   ms=mirpb.MirStorage.MIR_METADATAS,
                                                   mir_task_id=mir_task_id,
                                                   as_dict=True)
        return mir_storage_data

    @classmethod
    def _gen_viz_hist(cls, hist_dict: Any) -> List[Dict]:
        return sorted([{'x': k, 'y': v} for k, v in hist_dict.items()], key=lambda e: e['x'])

    @classmethod
    def _load_single_dataset_pred_or_gt_info(cls, mir_storage_context: mirpb.MirContext, task_storage: mirpb.Task,
                                             class_id_mgr: class_ids.ClassIdManager, is_gt: bool) -> dict:
        anno_stats = mir_storage_context.gt_stats if is_gt else mir_storage_context.pred_stats
        return dict(
            class_ids_count={k: v
                             for k, v in anno_stats.class_ids_cnt.items()},
            tags_count_total={k: v.cnt
                              for k, v in anno_stats.tags_cnt.items()},
            tags_count={k: {k2: v2
                            for k2, v2 in v.sub_cnt.items()}
                        for k, v in anno_stats.tags_cnt.items()},
            hist=dict(
                anno_quality=cls._gen_viz_hist(anno_stats.quality_hist),
                anno_area=cls._gen_viz_hist(anno_stats.area_hist),
                anno_area_ratio=cls._gen_viz_hist(anno_stats.area_ratio_hist),
            ),
            annos_count=anno_stats.total_cnt,
            negative_assets_count=anno_stats.negative_asset_cnt,
        )


def create_task(task_type: 'mirpb.TaskType.V',
                task_id: str,
                message: str,
                new_types: Dict[str, int] = {},
                new_types_added: bool = False,
                return_code: int = 0,
                return_msg: str = '',
                serialized_task_parameters: str = '',
                serialized_executor_config: str = '',
                executor: str = '',
                model_meta: mirpb.ModelMeta = None,
                evaluation: mirpb.Evaluation = None,
                src_revs: str = '',
                dst_rev: str = '') -> mirpb.Task:
    task_dict = {
        'type': task_type,
        'name': message,
        'task_id': task_id,
        'timestamp': int(time.time()),
        'return_code': return_code,
        'return_msg': return_msg,
        'serialized_task_parameters': serialized_task_parameters,
        'serialized_executor_config': serialized_executor_config,
        'new_types': new_types,
        'new_types_added': new_types_added,
        'executor': executor,
        'src_revs': src_revs,
        'dst_rev': dst_rev,
    }
    task: mirpb.Task = mirpb.Task()
    json_format.ParseDict(task_dict, task)

    if model_meta:
        task.model.CopyFrom(model_meta)

    if evaluation:
        task.evaluation.CopyFrom(evaluation)

    return task

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
from mir.tools import class_ids, context, det_eval, exodus, mir_storage, mir_repo_utils, revs_parser
from mir.tools import settings as mir_settings
from mir.tools.code import MirCode
from mir.tools.errors import MirError, MirRuntimeError


class MirStorageOpsBuildConfig:
    def __init__(self,
                 evaluate_conf_thr: float = mir_settings.DEFAULT_EVALUATE_CONF_THR,
                 evaluate_iou_thrs: str = mir_settings.DEFAULT_EVALUATE_IOU_THR,
                 evaluate_need_pr_curve: bool = False,
                 evaluate_src_dataset_id: str = '') -> None:
        self.evaluate_conf_thr: float = evaluate_conf_thr
        self.evaluate_iou_thrs: str = evaluate_iou_thrs
        self.evaluate_need_pr_curve: bool = evaluate_need_pr_curve
        self.evaluate_src_dataset_id: str = evaluate_src_dataset_id


class MirStorageOps():
    # private: save and load
    @classmethod
    def __build_and_save(cls, mir_root: str, mir_datas: Dict['mirpb.MirStorage.V', Any],
                         build_config: MirStorageOpsBuildConfig) -> None:
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

        if (mir_metadatas.attributes and mir_annotations.ground_truth.image_annotations
                and mir_annotations.task_annotations[mir_annotations.head_task_id].image_annotations):
            evaluation, _ = det_eval.det_evaluate_with_pb(
                mir_metadatas=mir_metadatas,
                mir_annotations=mir_annotations,
                mir_keywords=mir_keywords,
                dataset_id=build_config.evaluate_src_dataset_id,
                conf_thr=build_config.evaluate_conf_thr,
                iou_thrs=build_config.evaluate_iou_thrs,
                need_pr_curve=build_config.evaluate_need_pr_curve,
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
        # TODO: FUNCTION TO BE REMOVED
        task_annotations_count = len(mir_annotations.task_annotations)
        if task_annotations_count == 0:
            mir_annotations.task_annotations[head_task_id].CopyFrom(mirpb.SingleTaskAnnotations())
        elif task_annotations_count == 1:
            task_id = list(mir_annotations.task_annotations.keys())[0]
            if task_id != head_task_id:
                raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                      error_message=f"annotation head task id mismatch: {head_task_id} != {task_id}")
        elif task_annotations_count > 1:
            # * now we allows only one task id in each mir_annotations
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_REPO,
                                  error_message='more then one task ids found in mir_annotations')

        mir_annotations.head_task_id = head_task_id

    @classmethod
    def __build_mir_keywords(cls, mir_metadatas: mirpb.MirMetadatas, mir_annotations: mirpb.MirAnnotations,
                             mir_keywords: mirpb.MirKeywords) -> None:
        """
        build mir_keywords from single_task_annotations

        Args:
            single_task_annotations (mirpb.SingleTaskAnnotations)
            mir_keywords (mirpb.MirKeywords)
        """
        pred_task_annotations = mir_annotations.task_annotations[mir_annotations.head_task_id]

        for asset_id in mir_metadatas.attributes:
            pred_cis_set = set()
            gt_cis_set = set()

            if asset_id in pred_task_annotations.image_annotations:
                image_annotation = pred_task_annotations.image_annotations[asset_id]
                pred_cis_set.update([annotation.class_id for annotation in image_annotation.annotations])
            if asset_id in mir_annotations.ground_truth.image_annotations:
                image_annotation = mir_annotations.ground_truth.image_annotations[asset_id]
                gt_cis_set.update([annotation.class_id for annotation in image_annotation.annotations])

            if pred_cis_set:
                mir_keywords.keywords[asset_id].predefined_keyids[:] = pred_cis_set
            if gt_cis_set:
                mir_keywords.keywords[asset_id].gt_predefined_keyids[:] = gt_cis_set

        cls.__build_mir_keywords_ci_tag(task_annotations=pred_task_annotations, keyword_to_index=mir_keywords.pred_idx)
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
    def __build_mir_context_stats(cls, stats: mirpb.AnnoStats, mir_metadatas: mirpb.MirMetadatas,
                                  task_annotations: mirpb.SingleTaskAnnotations) -> None:
        image_annotations = task_annotations.image_annotations

        # pred_stats.asset_cnt
        stats.positive_asset_cnt = len(image_annotations)
        stats.negative_asset_cnt = len(mir_metadatas.attributes) - len(image_annotations)

        # pred_stats.quality_hist
        all_annotations = [
            annotation for image_annotation in image_annotations.values() for annotation in image_annotation.annotations
        ]
        stats.total_cnt = len(all_annotations)
        anno_quality_hist: Dict[float, int] = cls.__build_hist(
            values=[annotation.anno_quality for annotation in all_annotations],
            desc_lower_bnds=mir_settings.QUALITY_DESC_LOWER_BNDS)
        stats.quality_hist.update({f"{k:.2f}": v for k, v in anno_quality_hist.items()})

        # pred_stats.area_hist
        anno_area_hist: Dict[int, int] = cls.__build_hist(
            values=[annotation.box.w * annotation.box.h for annotation in all_annotations],
            desc_lower_bnds=mir_settings.ANNO_AREA_DESC_LOWER_BNDS)
        stats.area_hist.update(anno_area_hist)

        # pred_stats.area_ratio_hist
        all_area_ratios = []
        for asset_id, image_annotation in image_annotations.items():
            attrs = mir_metadatas.attributes[asset_id]
            asset_area = attrs.width * attrs.height
            for annotation in image_annotation.annotations:
                all_area_ratios.append(annotation.box.w * annotation.box.h / asset_area if asset_area else -1)
        anno_area_ratio_hist = cls.__build_hist(values=all_area_ratios,
                                                desc_lower_bnds=mir_settings.QUALITY_DESC_LOWER_BNDS)
        stats.area_ratio_hist.update({f"{k:.2f}": v for k, v in anno_area_ratio_hist.items()})

    @classmethod
    def __build_mir_context(cls, mir_metadatas: mirpb.MirMetadatas, mir_annotations: mirpb.MirAnnotations,
                            mir_keywords: mirpb.MirKeywords, project_class_ids: List[int],
                            mir_context: mirpb.MirContext) -> None:
        # ci to asset count
        for ci, ci_assets in mir_keywords.pred_idx.cis.items():
            mir_context.predefined_keyids_cnt[ci] = len(ci_assets.key_ids)

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
        image_annotations = mir_annotations.task_annotations[mir_annotations.head_task_id].image_annotations
        mir_context.images_cnt = len(mir_metadatas.attributes)
        mir_context.negative_images_cnt = mir_context.images_cnt - len(image_annotations)
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

        # tags cnt
        for tag, tag_to_annos in mir_keywords.pred_idx.tags.items():
            for anno_idxes in tag_to_annos.asset_annos.values():
                mir_context.tags_cnt[tag].cnt += len(anno_idxes.ids)

            for sub_tag, sub_tag_to_annos in tag_to_annos.sub_indexes.items():
                for anno_idxes in sub_tag_to_annos.key_ids.values():
                    mir_context.tags_cnt[tag].sub_cnt[sub_tag] += len(anno_idxes.ids)

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
        cls.__build_mir_context_stats(stats=mir_context.pred_stats,
                                      mir_metadatas=mir_metadatas,
                                      task_annotations=mir_annotations.task_annotations[mir_annotations.head_task_id])
        cls.__build_mir_context_stats(stats=mir_context.gt_stats,
                                      mir_metadatas=mir_metadatas,
                                      task_annotations=mir_annotations.ground_truth)

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
                        build_config: MirStorageOpsBuildConfig = MirStorageOpsBuildConfig()) -> int:
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
            conf_thr (float): confidence thr used to evaluate
            iou_thrs (str): iou thrs used to evaluate

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
        if not build_config.evaluate_src_dataset_id:
            build_config.evaluate_src_dataset_id = revs_parser.join_rev_tid(mir_branch, task.task_id)

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

            cls.__build_and_save(mir_root=mir_root, mir_datas=mir_datas, build_config=build_config)

            ret_code = CmdCommit.run_with_args(mir_root=mir_root, msg=task.name)
            if ret_code != MirCode.RC_OK:
                return ret_code

            # also have a tag for this commit
            cls.__add_git_tag(mir_root=mir_root, tag=revs_parser.join_rev_tid(mir_branch, task.task_id))

        return ret_code

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
            "total_asset_mbytes":222,
            "total_assets_cnt":1420,
            "hist":{
                "asset_quality": [],
                "asset_bytes": [],
                "asset_area": [],
                "asset_hw_ratio": [],
            },
            "pred":{
                "class_ids_count":{},
                "class_names_count":{},
                "new_types":{},
                "new_types_added":False,
                "negative_info":{
                    "negative_images_cnt":14,
                    "project_negative_images_cnt":0
                },
                "total_images_cnt":1420,
                "cks_count_total":{},
                "cks_count":{},
                "tags_cnt_total":{},
                "tags_cnt":{},
                "hist":{
                    "anno_quality":[],
                    "anno_area":[],
                    "anno_area_ratio":[]
                },
                "annos_cnt":10006,
                "positive_asset_cnt":1406,
                "negative_asset_cnt":14
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
        pred = dict(
            class_ids_count={k: v
                             for k, v in mir_storage_context.predefined_keyids_cnt.items()},
            class_names_count={
                class_id_mgr.main_name_for_id(id): count
                for id, count in mir_storage_context.predefined_keyids_cnt.items()
            },
            new_types={k: v
                       for k, v in task_storage.new_types.items()},
            new_types_added=task_storage.new_types_added,
            negative_info=dict(
                negative_images_cnt=mir_storage_context.negative_images_cnt,
                project_negative_images_cnt=mir_storage_context.project_negative_images_cnt,
            ),
            total_images_cnt=mir_storage_context.images_cnt,
            cks_count_total={k: v.cnt
                             for k, v in mir_storage_context.cks_cnt.items()},
            cks_count={k: {k2: v2
                           for k2, v2 in v.sub_cnt.items()}
                       for k, v in mir_storage_context.cks_cnt.items()},
            tags_cnt_total={k: v.cnt
                            for k, v in mir_storage_context.tags_cnt.items()},
            tags_cnt={k: {k2: v2
                          for k2, v2 in v.sub_cnt.items()}
                      for k, v in mir_storage_context.tags_cnt.items()},
            hist=dict(
                anno_quality=cls._gen_viz_hist(mir_storage_context.pred_stats.quality_hist),
                anno_area=cls._gen_viz_hist(mir_storage_context.pred_stats.area_hist),
                anno_area_ratio=cls._gen_viz_hist(mir_storage_context.pred_stats.area_ratio_hist),
            ),
            annos_cnt=mir_storage_context.pred_stats.total_cnt,
            positive_asset_cnt=mir_storage_context.pred_stats.positive_asset_cnt,
            negative_asset_cnt=mir_storage_context.pred_stats.negative_asset_cnt,
        )
        result = dict(
            total_asset_mbytes=mir_storage_context.total_asset_mbytes,
            total_assets_cnt=mir_storage_context.images_cnt,
            hist=dict(
                asset_quality=cls._gen_viz_hist(mir_storage_context.asset_quality_hist),
                asset_bytes=cls._gen_viz_hist(mir_storage_context.asset_bytes_hist),
                asset_area=cls._gen_viz_hist(mir_storage_context.asset_area_hist),
                asset_hw_ratio=cls._gen_viz_hist(mir_storage_context.asset_hw_ratio_hist),
            ),
            pred=pred,
            gt={},
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
        hid = mir_storage_annotations["head_task_id"]
        if "task_annotations" in mir_storage_annotations:
            pred_annotations = mir_storage_annotations["task_annotations"][hid]["image_annotations"]
        else:
            pred_annotations = {}
        if "ground_truth" in mir_storage_annotations:
            gt_annotations = mir_storage_annotations['ground_truth'].get('image_annotations', {})
        else:
            gt_annotations = {}
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
            pred_class_ids_index={k: v.get('key_ids')
                                  for k, v in mir_storage_keywords.get('pred_idx', {}).get('cis', {}).items()},
            gt_class_ids_index={k: v.get('key_ids')
                                for k, v in mir_storage_keywords.get('gt_idx', {}).get('cis', {}).items()},
        )

    @classmethod
    def load_dataset_evaluations(cls, mir_root: str, mir_branch: str, mir_task_id: str = '') -> Dict:
        mir_storage_data: mirpb.MirTasks = cls.load_single_storage(mir_root=mir_root,
                                                                   mir_branch=mir_branch,
                                                                   ms=mirpb.MirStorage.MIR_TASKS,
                                                                   mir_task_id=mir_task_id,
                                                                   as_dict=False)
        task = mir_storage_data.tasks[mir_storage_data.head_task_id]
        if not task.evaluation.dataset_evaluations:
            raise MirError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="no dataset evaluation")

        dataset_evaluations = cls.__message_to_dict(task.evaluation)
        return dataset_evaluations["dataset_evaluations"]

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
        return sorted([{'x': k, 'y': v} for k, v in hist_dict.items()], key=lambda e: e['x']),  # type: ignore


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

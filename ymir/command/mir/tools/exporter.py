from collections import defaultdict
from datetime import datetime
from functools import partial
import json
import os
import shutil
from typing import Dict, List, Optional, Protocol, TextIO, Tuple, Union
import uuid
import xml.etree.ElementTree as ElementTree

import numpy as np
from pycocotools import mask as mask_utils

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import annotations, mir_storage
from mir.tools.class_ids import UserLabels
from mir.tools.code import MirCode, time_it
from mir.tools.errors import MirRuntimeError
from mir.tools.settings import COCO_JSON_NAME


def _asset_file_ext(asset_format: "mirpb.AssetType.V") -> str:
    _asset_ext_map = {
        mirpb.AssetType.AssetTypeImageJpeg: 'jpg',
        mirpb.AssetType.AssetTypeImagePng: 'png',
        mirpb.AssetType.AssetTypeImageBmp: 'bmp',
    }
    return _asset_ext_map.get(asset_format, "unknown")


def _anno_file_ext(anno_format: "mirpb.ExportFormat.V") -> str:
    _anno_ext_map = {
        mirpb.ExportFormat.EF_ARK_TXT: 'txt',
        mirpb.ExportFormat.EF_VOC_XML: 'xml',
        mirpb.ExportFormat.EF_LS_JSON: 'json',
        mirpb.ExportFormat.EF_COCO_JSON: 'json',
    }
    return _anno_ext_map.get(anno_format, "unknown")


class _SingleTaskAnnotationCallable(Protocol):
    def __call__(self, mir_metadatas: mirpb.MirMetadatas, task_annotations: mirpb.SingleTaskAnnotations,
                 ec: mirpb.ExportConfig, class_ids_mapping: Optional[Dict[int, int]], cls_id_mgr: Optional[UserLabels],
                 dst_dir: str, image_cks: Dict[str, mirpb.SingleImageCks]) -> None:
        ...


class _SingleImageAnnotationCallable(Protocol):
    def __call__(self, attributes: mirpb.MetadataAttributes, image_annotations: mirpb.SingleImageAnnotations,
                 image_cks: Optional[mirpb.SingleImageCks], class_ids_mapping: Optional[Dict[int, int]],
                 cls_id_mgr: Optional[UserLabels], asset_filename: str, anno_dst_file: str) -> None:
        ...


def _task_annotations_output_func(
    anno_format: "mirpb.ExportFormat.V"
) -> _SingleTaskAnnotationCallable:
    _format_func_map: Dict["mirpb.ExportFormat.V", _SingleTaskAnnotationCallable] = {
        mirpb.ExportFormat.EF_ARK_TXT: _single_task_annotations_to_ark,
        mirpb.ExportFormat.EF_VOC_XML: _single_task_annotations_to_voc,
        mirpb.ExportFormat.EF_LS_JSON: _single_task_annotations_to_ls,
        mirpb.ExportFormat.EF_COCO_JSON: _single_task_annotations_to_coco,
    }
    if anno_format not in _format_func_map:
        raise NotImplementedError(f"unknown anno_format: {anno_format}")
    return _format_func_map[anno_format]


def parse_asset_format(asset_format_str: str) -> "mirpb.AssetFormat.V":
    _asset_dict: Dict[str, mirpb.AssetFormat.V] = {
        "raw": mirpb.AssetFormat.AF_RAW,
        "lmdb": mirpb.AssetFormat.AF_LMDB,
    }
    return _asset_dict.get(asset_format_str.lower(), mirpb.AssetFormat.AF_UNKNOWN)


def parse_export_type(type_str: str) -> Tuple["mirpb.ExportFormat.V", "mirpb.AssetFormat.V"]:
    if not type_str:
        return (mirpb.ExportFormat.EF_VOC_XML, mirpb.AssetFormat.AF_RAW)

    anno_str, asset_str = type_str.split(':')
    return (annotations.parse_anno_format(anno_str), parse_asset_format(asset_str))


def get_index_filename(is_asset: bool = True,
                       is_pred: bool = False,
                       tvt_type: Optional["mirpb.TvtType.V"] = None) -> str:
    index_filename = "index.tsv"
    if is_asset:
        return index_filename

    if tvt_type:
        _tvt_type_prefix: Dict["mirpb.TvtType.V", str] = {
            mirpb.TvtType.TvtTypeTraining: "train",
            mirpb.TvtType.TvtTypeValidation: "val",
            mirpb.TvtType.TvtTypeTest: "test",
        }
        index_filename = f"{_tvt_type_prefix[tvt_type]}-{index_filename}"

    if is_pred:
        index_filename = "pred-" + index_filename

    return index_filename


def _gen_abs_idx_file_path(abs_dir: str,
                           idx_prefix: str,
                           file_name: str,
                           file_ext: str,
                           need_sub_folder: bool,) -> Tuple[str, str]:
    abs_path: str = mir_storage.get_asset_storage_path(location=abs_dir,
                                                       hash=file_name,
                                                       make_dirs=True,
                                                       need_sub_folder=need_sub_folder)
    abs_file = f"{abs_path}.{file_ext}"
    index_path: str = mir_storage.get_asset_storage_path(location=idx_prefix,
                                                         hash=file_name,
                                                         make_dirs=False,
                                                         need_sub_folder=need_sub_folder)
    idx_file = f"{index_path}.{file_ext}"
    return (abs_file, idx_file)


@time_it
def export_mirdatas_to_dir(
    mir_metadatas: mirpb.MirMetadatas,
    ec: mirpb.ExportConfig,
    mir_annotations: Optional[mirpb.MirAnnotations] = None,
    class_ids_mapping: Optional[Dict[int, int]] = None,
    cls_id_mgr: Optional[UserLabels] = None,
) -> int:
    if not (ec.asset_dir and ec.media_location and os.path.isdir(ec.media_location)):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"invalid export config {ec}")
    os.makedirs(ec.asset_dir, exist_ok=True)

    if ec.asset_format == mirpb.AssetFormat.AF_LMDB:
        return _export_mirdatas_to_lmdb(
            mir_metadatas=mir_metadatas,
            ec=ec,
            mir_annotations=mir_annotations,
            class_ids_mapping=class_ids_mapping,
            cls_id_mgr=cls_id_mgr,
        )
    elif ec.asset_format == mirpb.AssetFormat.AF_RAW:
        return _export_mirdatas_to_raw(
            mir_metadatas=mir_metadatas,
            ec=ec,
            mir_annotations=mir_annotations,
            class_ids_mapping=class_ids_mapping,
            cls_id_mgr=cls_id_mgr,
        )

    raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                          error_message=f"unknown asset format: {ec.asset_format}")


def _export_mirdatas_to_raw(
    mir_metadatas: mirpb.MirMetadatas,
    ec: mirpb.ExportConfig,
    mir_annotations: Optional[mirpb.MirAnnotations] = None,
    class_ids_mapping: Optional[Dict[int, int]] = None,
    cls_id_mgr: Optional[UserLabels] = None,
) -> int:
    # Setup path and file handler.
    ec.asset_index_file = ec.asset_index_file or os.path.join(ec.asset_dir, get_index_filename())
    ec.asset_index_prefix = ec.asset_index_prefix or ec.asset_dir
    index_asset_f = open(ec.asset_index_file, 'w')

    index_gt_f = None
    if ec.gt_dir:
        if not ec.gt_index_file:
            ec.gt_index_file = os.path.join(ec.gt_dir, get_index_filename())
        os.makedirs(ec.gt_dir, exist_ok=True)
        index_gt_f = open(ec.gt_index_file, 'w')
        ec.gt_index_prefix = ec.gt_index_prefix or ec.gt_dir

    index_pred_f = None
    if ec.pred_dir:
        if not ec.pred_index_file:
            ec.pred_index_file = os.path.join(ec.pred_dir, get_index_filename())
        os.makedirs(ec.pred_dir, exist_ok=True)
        index_pred_f = open(ec.pred_index_file, 'w')
        ec.pred_index_prefix = ec.pred_index_prefix or ec.pred_dir

    index_tvt_f: Dict[Tuple[bool, "mirpb.TvtType.V"], TextIO] = {}
    if ec.tvt_index_dir:
        os.makedirs(ec.tvt_index_dir, exist_ok=True)
        for is_pred in [True, False]:
            for tvt_type in [mirpb.TvtType.TvtTypeTraining, mirpb.TvtType.TvtTypeValidation, mirpb.TvtType.TvtTypeTest]:
                file_name = get_index_filename(is_asset=False, is_pred=is_pred, tvt_type=tvt_type)
                index_tvt_f[(is_pred, tvt_type)] = open(os.path.join(ec.tvt_index_dir, file_name), 'w')

    for asset_id, attributes in mir_metadatas.attributes.items():
        # export asset.
        asset_src_file: str = mir_storage.locate_asset_path(location=ec.media_location, hash=asset_id)
        asset_abs_file, asset_idx_file = _gen_abs_idx_file_path(abs_dir=ec.asset_dir,
                                                                idx_prefix=ec.asset_index_prefix,
                                                                file_name=asset_id,
                                                                file_ext=_asset_file_ext(attributes.asset_type),
                                                                need_sub_folder=ec.need_sub_folder)
        if not os.path.isfile(asset_abs_file) or os.stat(asset_src_file).st_size != os.stat(asset_abs_file).st_size:
            shutil.copyfile(asset_src_file, asset_abs_file)
        index_asset_f.write(f"{asset_idx_file}\n")

    if ec.anno_format != mirpb.ExportFormat.EF_NO_ANNOTATIONS and mir_annotations:
        # export annotations
        _output_func = _task_annotations_output_func(ec.anno_format)
        if ec.pred_dir:
            _output_func(
                mir_metadatas=mir_metadatas,
                task_annotations=mir_annotations.prediction,
                ec=ec,
                class_ids_mapping=class_ids_mapping,
                cls_id_mgr=cls_id_mgr,
                dst_dir=ec.pred_dir,
                image_cks={},
            )
        if ec.gt_dir:
            _output_func(
                mir_metadatas=mir_metadatas,
                task_annotations=mir_annotations.ground_truth,
                ec=ec,
                class_ids_mapping=class_ids_mapping,
                cls_id_mgr=cls_id_mgr,
                dst_dir=ec.gt_dir,
                image_cks=dict(mir_annotations.image_cks),
            )

        # write index tsv files
        for asset_id, attributes in mir_metadatas.attributes.items():
            _, asset_idx_file = _gen_abs_idx_file_path(abs_dir=ec.asset_dir,
                                                       idx_prefix=ec.asset_index_prefix,
                                                       file_name=asset_id,
                                                       file_ext=_asset_file_ext(attributes.asset_type),
                                                       need_sub_folder=ec.need_sub_folder)
            if index_gt_f:
                if ec.anno_format == mirpb.ExportFormat.EF_COCO_JSON:
                    _, gt_idx_file = _gen_abs_idx_file_path(abs_dir=ec.gt_dir,
                                                            idx_prefix=ec.gt_index_prefix,
                                                            file_name='coco-annotations',
                                                            file_ext='json',
                                                            need_sub_folder=False)
                else:
                    _, gt_idx_file = _gen_abs_idx_file_path(abs_dir=ec.gt_dir,
                                                            idx_prefix=ec.gt_index_prefix,
                                                            file_name=asset_id,
                                                            file_ext=_anno_file_ext(anno_format=ec.anno_format),
                                                            need_sub_folder=ec.need_sub_folder)
                asset_anno_pair_line = f"{asset_idx_file}\t{gt_idx_file}\n"

                index_gt_f.write(asset_anno_pair_line)
                if ec.tvt_index_dir:
                    index_tvt_f[(False, attributes.tvt_type)].write(asset_anno_pair_line)
            if index_pred_f:
                if ec.anno_format == mirpb.ExportFormat.EF_COCO_JSON:
                    _, pred_idx_file = _gen_abs_idx_file_path(abs_dir=ec.pred_dir,
                                                              idx_prefix=ec.pred_index_prefix,
                                                              file_name='coco-annotations',
                                                              file_ext='json',
                                                              need_sub_folder=False)
                else:
                    _, pred_idx_file = _gen_abs_idx_file_path(abs_dir=ec.pred_dir,
                                                              idx_prefix=ec.pred_index_prefix,
                                                              file_name=asset_id,
                                                              file_ext=_anno_file_ext(anno_format=ec.anno_format),
                                                              need_sub_folder=ec.need_sub_folder)
                asset_anno_pair_line = f"{asset_idx_file}\t{pred_idx_file}\n"

                index_pred_f.write(asset_anno_pair_line)
                if index_tvt_f:
                    index_tvt_f[(True, attributes.tvt_type)].write(asset_anno_pair_line)

    index_asset_f.close()
    # Clean up.
    if index_gt_f:
        index_gt_f.close()
    if index_pred_f:
        index_pred_f.close()
    for single_idx_f in index_tvt_f.values():
        single_idx_f.close()

    return MirCode.RC_OK


def _export_mirdatas_to_lmdb(
    mir_metadatas: mirpb.MirMetadatas,
    ec: mirpb.ExportConfig,
    mir_annotations: Optional[mirpb.MirAnnotations] = None,
    class_ids_mapping: Optional[Dict[int, int]] = None,
    cls_id_mgr: Optional[UserLabels] = None,
) -> int:
    raise NotImplementedError("LMDB format is not supported yet.")


# single image annotations export functions
def _single_image_annotations_to_det_ark(attributes: mirpb.MetadataAttributes,
                                         image_annotations: mirpb.SingleImageAnnotations,
                                         image_cks: Optional[mirpb.SingleImageCks],
                                         class_ids_mapping: Optional[Dict[int, int]],
                                         cls_id_mgr: Optional[UserLabels], asset_filename: str,
                                         anno_dst_file: str) -> None:
    output_str = ""
    for annotation in image_annotations.boxes:
        if class_ids_mapping and annotation.class_id not in class_ids_mapping:
            continue

        mapped_id = class_ids_mapping[annotation.class_id] if class_ids_mapping else annotation.class_id
        output_str += f"{mapped_id}, {annotation.box.x}, {annotation.box.y}, "
        output_str += f"{annotation.box.x + annotation.box.w - 1}, {annotation.box.y + annotation.box.h - 1}, "
        output_str += f"{annotation.anno_quality}, {annotation.box.rotate_angle}\n"

    with open(anno_dst_file, 'w') as af:
        af.write(output_str)


def _single_image_annotations_to_voc(attributes: mirpb.MetadataAttributes,
                                     image_annotations: mirpb.SingleImageAnnotations,
                                     image_cks: Optional[mirpb.SingleImageCks],
                                     class_ids_mapping: Optional[Dict[int, int]], cls_id_mgr: Optional[UserLabels],
                                     asset_filename: str, anno_dst_file: str) -> None:
    if not cls_id_mgr:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="invalid cls_id_mgr.")

    annotations = image_annotations.boxes

    # annotation
    annotation_node = ElementTree.Element('annotation')

    # annotation: folder
    folder_node = ElementTree.SubElement(annotation_node, 'folder')
    folder_node.text = 'folder'

    # annotation: filename
    filename_node = ElementTree.SubElement(annotation_node, 'filename')
    filename_node.text = asset_filename

    # annotation: source
    source_node = ElementTree.SubElement(annotation_node, 'source')

    # annotation: source: annotation
    annotation2_node = ElementTree.SubElement(source_node, 'annotation')
    annotation2_node.text = 'unknown'

    # annotation: source: image
    image_node = ElementTree.SubElement(source_node, 'image')
    image_node.text = 'unknown'

    # annotation: size
    size_node = ElementTree.SubElement(annotation_node, 'size')

    # annotation: size: width
    width_node = ElementTree.SubElement(size_node, 'width')
    width_node.text = str(attributes.width)

    # annotation: size: height
    height_node = ElementTree.SubElement(size_node, 'height')
    height_node.text = str(attributes.height)

    # annotation: size: depth
    depth_node = ElementTree.SubElement(size_node, 'depth')
    depth_node.text = str(attributes.image_channels)

    # annotation: segmented
    segmented_node = ElementTree.SubElement(annotation_node, 'segmented')
    segmented_node.text = '0'

    # annotation: cks and sub nodes
    if image_cks:
        if image_cks.cks:
            cks_node = ElementTree.SubElement(annotation_node, 'cks')
            for k, v in image_cks.cks.items():
                ElementTree.SubElement(cks_node, k).text = v

        # annotation: image_quality
        image_quality_node = ElementTree.SubElement(annotation_node, 'image_quality')
        image_quality_node.text = f"{image_cks.image_quality:.4f}"

    # annotation: object(s)
    for annotation in annotations:
        if class_ids_mapping and annotation.class_id not in class_ids_mapping:
            continue

        object_node = ElementTree.SubElement(annotation_node, 'object')

        name_node = ElementTree.SubElement(object_node, 'name')
        name_node.text = cls_id_mgr.main_name_for_id(annotation.class_id)

        pose_node = ElementTree.SubElement(object_node, 'pose')
        pose_node.text = 'unknown'

        truncated_node = ElementTree.SubElement(object_node, 'truncated')
        truncated_node.text = 'unknown'

        occluded_node = ElementTree.SubElement(object_node, 'occluded')
        occluded_node.text = '0'

        w, h = annotation.box.w, annotation.box.h
        if w and h:  # det box
            bndbox_node = ElementTree.SubElement(object_node, 'bndbox')

            xmin_node = ElementTree.SubElement(bndbox_node, 'xmin')
            xmin_node.text = str(annotation.box.x)

            ymin_node = ElementTree.SubElement(bndbox_node, 'ymin')
            ymin_node.text = str(annotation.box.y)

            xmax_node = ElementTree.SubElement(bndbox_node, 'xmax')
            xmax_node.text = str(annotation.box.x + w - 1)

            ymax_node = ElementTree.SubElement(bndbox_node, 'ymax')
            ymax_node.text = str(annotation.box.y + h - 1)

            rotate_angle_node = ElementTree.SubElement(bndbox_node, 'rotate_angle')
            rotate_angle_node.text = f"{annotation.box.rotate_angle:.4f}"
        elif len(annotation.polygon) > 0:  # seg polygon
            raise NotImplementedError

        difficult_node = ElementTree.SubElement(object_node, 'difficult')
        difficult_node.text = '0'

        if annotation.tags:  # Not add tags node if empty, otherwise xmlparse lib will get tags: None.
            tags_node = ElementTree.SubElement(object_node, 'tags')
            for k, v in annotation.tags.items():
                ElementTree.SubElement(tags_node, k).text = v

        box_quality_node = ElementTree.SubElement(object_node, 'box_quality')
        box_quality_node.text = f"{annotation.anno_quality:.4f}"

        if annotation.cm != mirpb.ConfusionMatrixType.NotSet:
            cm_node = ElementTree.SubElement(object_node, 'cm')
            cm_node.text = f"{mirpb.ConfusionMatrixType.Name(annotation.cm)}"

        confidence_node = ElementTree.SubElement(object_node, 'confidence')
        confidence_node.text = f"{annotation.score:.4f}"

    with open(anno_dst_file, 'w') as af:
        af.write(ElementTree.tostring(element=annotation_node, encoding='unicode'))


def _single_image_annotations_to_det_ls_json(attributes: mirpb.MetadataAttributes,
                                             image_annotations: mirpb.SingleImageAnnotations,
                                             image_cks: Optional[mirpb.SingleImageCks],
                                             class_ids_mapping: Optional[Dict[int, int]],
                                             cls_id_mgr: Optional[UserLabels], asset_filename: str,
                                             anno_dst_file: str) -> None:
    if not cls_id_mgr:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="invalid cls_id_mgr.")

    annotations = image_annotations.boxes

    out_type = "predictions"  # out_type: annotation type - "annotations" or "predictions"
    to_name = 'image'  # to_name: object name from Label Studio labeling config
    from_name = 'label'  # control tag name from Label Studio labeling config
    task: Dict = {
        out_type: [{
            "result": [],
            "ground_truth": False,
        }],
        "data": {
            "image": asset_filename
        }
    }

    for annotation in annotations:
        if class_ids_mapping and annotation.class_id not in class_ids_mapping:
            continue

        img_width, img_height = attributes.width, attributes.height
        if annotation.type == mirpb.ObjectSubType.OST_NOTSET:
            # detection
            bbox_x, bbox_y = float(annotation.box.x), float(annotation.box.y)
            bbox_width, bbox_height = float(annotation.box.w), float(annotation.box.h)
            result_item = {
                "id": uuid.uuid4().hex[0:10],  # random id to identify this annotation.
                "type": "rectanglelabels",
                "value": {
                    # Units of image annotations in label studio is percentage of image width/height.
                    # https://labelstud.io/guide/predictions.html#Units-of-image-annotations
                    "x": bbox_x / img_width * 100,
                    "y": bbox_y / img_height * 100,
                    "width": bbox_width / img_width * 100,
                    "height": bbox_height / img_height * 100,
                    "rotation": 0,
                    "rectanglelabels": [cls_id_mgr.main_name_for_id(annotation.class_id)]
                },
                "to_name": to_name,
                "from_name": from_name,
                "image_rotation": 0,
                "original_width": img_width,
                "original_height": img_height
            }
        else:
            # segmentation
            result_item = {
                "id": uuid.uuid4().hex[0:10],  # random id to identify this annotation.
                "type": "brushlabels",
                "value": {
                    "format":
                    "rle",
                    "rle":
                    _coco_rle_to_ls_rle(
                        mask_or_polygon=(annotation.mask if annotation.type == mirpb.ObjectSubType.OST_SEG_MASK else
                                         list(annotation.polygon)),
                        width=img_width,
                        height=img_height,
                        img_name=f"{os.path.splitext(os.path.basename(anno_dst_file))[0]}-{annotation.class_id}.png"),
                    "brushlabels": [cls_id_mgr.main_name_for_id(annotation.class_id)]
                },
                "to_name": to_name,
                "from_name": from_name,
                "image_rotation": 0,
                "original_width": img_width,
                "original_height": img_height
            }
        task[out_type][0]['result'].append(result_item)

    with open(anno_dst_file, 'w') as af:
        af.write(json.dumps(task))


# single task annotations export functions
def _single_task_annotations_to_separated_any(
    mir_metadatas: mirpb.MirMetadatas,
    task_annotations: mirpb.SingleTaskAnnotations,
    ec: mirpb.ExportConfig,
    class_ids_mapping: Optional[Dict[int, int]],
    cls_id_mgr: Optional[UserLabels],
    dst_dir: str,
    image_cks: Dict[str, mirpb.SingleImageCks],
    single_image_func: _SingleImageAnnotationCallable,
) -> None:
    for asset_id, attributes in mir_metadatas.attributes.items():
        _, asset_idx_file = _gen_abs_idx_file_path(abs_dir=ec.asset_dir,
                                                   idx_prefix=ec.asset_index_prefix,
                                                   file_name=asset_id,
                                                   file_ext=_asset_file_ext(attributes.asset_type),
                                                   need_sub_folder=ec.need_sub_folder)

        anno_abs_file, _ = _gen_abs_idx_file_path(abs_dir=dst_dir,
                                                  idx_prefix='',
                                                  file_name=asset_id,
                                                  file_ext=_anno_file_ext(anno_format=ec.anno_format),
                                                  need_sub_folder=ec.need_sub_folder)
        single_image_func(
            attributes=attributes,
            image_annotations=task_annotations.image_annotations.get(asset_id, mirpb.SingleImageAnnotations()),
            image_cks=image_cks.get(asset_id, mirpb.SingleImageCks()),
            class_ids_mapping=class_ids_mapping,
            cls_id_mgr=cls_id_mgr,
            asset_filename=asset_idx_file,
            anno_dst_file=anno_abs_file,
        )


_single_task_annotations_to_voc: _SingleTaskAnnotationCallable = partial(
    _single_task_annotations_to_separated_any, single_image_func=_single_image_annotations_to_voc)
_single_task_annotations_to_ls: _SingleTaskAnnotationCallable = partial(
    _single_task_annotations_to_separated_any, single_image_func=_single_image_annotations_to_det_ls_json)
_single_task_annotations_to_ark: _SingleTaskAnnotationCallable = partial(
    _single_task_annotations_to_separated_any, single_image_func=_single_image_annotations_to_det_ark)


def _single_task_annotations_to_coco(
    mir_metadatas: mirpb.MirMetadatas,
    task_annotations: mirpb.SingleTaskAnnotations,
    ec: mirpb.ExportConfig,  # noqa
    class_ids_mapping: Optional[Dict[int, int]],
    cls_id_mgr: Optional[UserLabels],
    dst_dir: str,
    image_cks: Dict[str, mirpb.SingleImageCks],  # noqa
) -> None:
    if not cls_id_mgr:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='invalid cls_id_mgr')

    if not class_ids_mapping:
        class_ids_mapping = {v: v for v in task_annotations.task_class_ids}
    # filter / remapping class ids and task_annotations.image_annotations
    categories_list = [{
        'id': class_ids_mapping[cid],
        'name': cls_id_mgr.main_name_for_id(cid),
        'supercategory': 'object',
    } for cid in task_annotations.task_class_ids if cid in class_ids_mapping]
    asset_id_to_image_annotations: Dict[str, List[mirpb.ObjectAnnotation]] = defaultdict(list)
    for asset_id, sia in task_annotations.image_annotations.items():
        for oa in sia.boxes:
            if oa.class_id in class_ids_mapping:
                oa.class_id = class_ids_mapping[oa.class_id]
                asset_id_to_image_annotations[asset_id].append(oa)

    # images list
    images_list = []
    asset_id_to_coco_image_ids: Dict[str, int] = {}
    for idx, asset_id in enumerate(sorted(mir_metadatas.attributes.keys())):
        attrs = mir_metadatas.attributes[asset_id]
        images_list.append({
            'id': idx + 1,
            'file_name': f"{asset_id}.{_asset_file_ext(attrs.asset_type)}",
            'width': attrs.width,
            'height': attrs.height,
            'date_captured': str(datetime.fromtimestamp(attrs.timestamp.start)),
            'license': 1,
            'coco_url': '',
            'flickr_url': '',
        })
        asset_id_to_coco_image_ids[asset_id] = idx + 1

    # licenses list: add placeholder here
    licenses_list = [{
        'id': 1,
        'name': '',
        'url': '',
    }]

    # annotations list
    annotations_list = []
    coco_anno_id = 1
    for asset_id, oas_list in asset_id_to_image_annotations.items():
        coco_image_id = asset_id_to_coco_image_ids[asset_id]
        attrs = mir_metadatas.attributes[asset_id]
        for oa in oas_list:
            segmentation: Union[list, dict] = {}
            if oa.type == mirpb.ObjectSubType.OST_SEG_MASK:
                segmentation = {
                    'counts': oa.mask,
                    'size': [attrs.height, attrs.width],
                }
            elif oa.type == mirpb.ObjectSubType.OST_SEG_POLYGON:
                segmentation = [[]]
                for p in oa.polygon:
                    segmentation[0].extend([p.x, p.y])

            annotations_list.append({
                'id': coco_anno_id,
                'image_id': coco_image_id,
                'category_id': oa.class_id,
                'iscrowd': oa.iscrowd,
                'bbox': [oa.box.x, oa.box.y, oa.box.w, oa.box.h],
                'segmentation': segmentation,
            })
            coco_anno_id += 1

    with open(os.path.join(dst_dir, COCO_JSON_NAME), 'w') as f:
        coco_dict = {
            'images': images_list,
            'licenses': licenses_list,
            'categories': categories_list,
            'annotations': annotations_list,
        }
        f.write(json.dumps(coco_dict))


# todo: we should have a file for rle converters
# if type(ann['segmentation']['counts']) == list:
#     rle = maskUtils.frPyObjects([ann['segmentation']], t['height'], t['width'])
# else:
#     rle = [ann['segmentation']]
# m = maskUtils.decode(rle)
def _coco_rle_to_ls_rle(mask_or_polygon: Union[str, List[mirpb.IntPoint]], width: int, height: int,
                        img_name: str) -> List[int]:
    if isinstance(mask_or_polygon, str):
        coco_seg = {'counts': mask_or_polygon, 'size': [height, width]}
    elif isinstance(mask_or_polygon, list):
        polygon = []
        for p in mask_or_polygon:
            polygon.extend([p.x, p.y])
        coco_seg = mask_utils.frPyObjects({'counts': [[polygon]]}, height, width)

    # coco_seg: dict -> mask: np.ndarray (shape: h * w * 1) -> ls_rle: List[int]
    return _mask2rle(mask_utils.decode(coco_seg) * 255)


def _mask2rle(mask: np.ndarray) -> List[int]:
    """ Convert mask to RLE

    :param mask: uint8 or int np.array mask with len(shape) == 2 like grayscale image
    :return: list of ints in RLE format
    """
    assert len(mask.shape) == 2, 'mask must be 2D np.array'
    assert mask.dtype == np.uint8 or mask.dtype == int, 'mask must be uint8 or int'
    array = mask.ravel()
    array = np.repeat(array, 4)  # must be 4 channels
    rle = _encode_rle(array)
    return rle


def _encode_rle(arr: np.ndarray, wordsize: int = 8, rle_sizes: List[int] = [3, 4, 8, 16]) -> List[int]:
    """ Encode a 1d array to rle
    :param arr: flattened np.array from a 4d image (R, G, B, alpha)
    :type arr: np.array
    :param wordsize: wordsize bits for decoding, default is 8
    :type wordsize: int
    :param rle_sizes:  list of ints which state how long a series is of the same number
    :type rle_sizes: list
        :return rle: run length encoded array
    :type rle: list
    """
    # Set length of array in 32 bits
    num = len(arr)
    numbits = f'{num:032b}'

    # put in the wordsize in bits
    wordsizebits = f'{wordsize - 1:05b}'

    # put rle sizes in the bits
    rle_bits = ''.join([f'{x - 1:04b}' for x in rle_sizes])

    # combine it into base string
    base_str = numbits + wordsizebits + rle_bits

    # start with creating the rle bite string
    out_str = ''
    for length_reeks, p, value in zip(*base_rle_encode(arr)):
        # TODO: A nice to have but --> this can be optimized but works
        if length_reeks == 1:
            # we state with the first 0 that it has a length of 1
            out_str += '0'
            # We state now the index on the rle sizes
            out_str += '00'

            # the rle size value is 0 for an individual number
            out_str += '000'

            # put the value in a 8 bit string
            out_str += f'{value:08b}'

        elif length_reeks > 1:
            # rle size = 3
            if length_reeks <= 8:
                # Starting with a 1 indicates that we have started a series
                out_str += '1'

                # index in rle size arr
                out_str += '00'

                # length of array to bits
                out_str += f'{length_reeks - 1:03b}'

                out_str += f'{value:08b}'

            # rle size = 4
            elif 8 < length_reeks <= 16:
                # Starting with a 1 indicates that we have started a series
                out_str += '1'
                out_str += '01'

                # length of array to bits
                out_str += f'{length_reeks - 1:04b}'

                out_str += f'{value:08b}'

            # rle size = 8
            elif 16 < length_reeks <= 256:
                # Starting with a 1 indicates that we have started a series
                out_str += '1'

                out_str += '10'

                # length of array to bits
                out_str += f'{length_reeks - 1:08b}'

                out_str += f'{value:08b}'

            # rle size = 16 or longer
            else:

                length_temp = length_reeks
                while length_temp > 2 ** 16:
                    # Starting with a 1 indicates that we have started a series
                    out_str += '1'

                    out_str += '11'
                    out_str += f'{2 ** 16 - 1:016b}'

                    out_str += f'{value:08b}'
                    length_temp -= 2 ** 16

                # Starting with a 1 indicates that we have started a series
                out_str += '1'

                out_str += '11'
                # length of array to bits
                out_str += f'{length_temp - 1:016b}'

                out_str += f'{value:08b}'

    # make sure that we have an 8 fold lenght otherwise add 0's at the end
    nzfill = 8 - len(base_str + out_str) % 8
    total_str = base_str + out_str
    total_str = total_str + nzfill * '0'

    rle = bits2byte(total_str)

    return rle


def base_rle_encode(inarray: np.ndarray) -> tuple:
    """ run length encoding. Partial credit to R rle function.
        Multi datatype arrays catered for including non Numpy
        returns: tuple (runlengths, startpositions, values) """
    ia = np.asarray(inarray)                # force numpy
    n = len(ia)
    if n == 0:
        return None, None, None
    else:
        y = ia[1:] != ia[:-1]                # pairwise unequal (string safe)
        i = np.append(np.where(y), n - 1)    # must include last element posi
        z = np.diff(np.append(-1, i))        # run lengths
        p = np.cumsum(np.append(0, z))[:-1]  # positions
        return z, p, ia[i]


def bits2byte(arr_str: str, n: int = 8) -> List[int]:
    """ Convert bits back to byte
    :param arr_str:  string with the bit array
    :type arr_str: str
    :param n: number of bits to separate the arr string into
    :type n: int
    :return rle:
    :type rle: list
    """
    rle = []
    numbers = [arr_str[i:i + n] for i in range(0, len(arr_str), n)]
    for i in numbers:
        rle.append(int(i, 2))
    return rle

import fileinput
import json
import os
import shutil
from typing import Callable, Dict, Optional, TextIO, Tuple
import uuid
import xml.etree.ElementTree as ElementTree

from mir.tools.class_ids import ClassIdManager
from mir.tools.code import MirCode
from mir.tools import annotations, mir_storage
from mir.protos import mir_command_pb2 as mirpb
from mir.tools.errors import MirRuntimeError


def _asset_file_ext(asset_format: "mirpb.AssetType.V") -> str:
    _asset_ext_map = {
        mirpb.AssetType.AssetTypeImageJpeg: 'jpg',
        mirpb.AssetType.AssetTypeImagePng: 'png',
        mirpb.AssetType.AssetTypeImageBmp: 'bmp',
    }
    return _asset_ext_map.get(asset_format, "unknown")


def _anno_file_ext(anno_format: "mirpb.AnnoFormat.V") -> str:
    _anno_ext_map = {
        mirpb.AnnoFormat.AF_DET_ARK_JSON: 'txt',
        mirpb.AnnoFormat.AF_DET_PASCAL_VOC: 'xml',
        mirpb.AnnoFormat.AF_DET_LS_JSON: 'json',
        mirpb.AnnoFormat.AF_SEG_POLYGON: 'xml',
        mirpb.AnnoFormat.AF_SEG_MASK: 'png',
    }
    return _anno_ext_map.get(anno_format, "unknown")


def _format_file_output_func(anno_format: "mirpb.AnnoFormat.V") -> Callable:
    _format_func_map = {
        mirpb.AnnoFormat.AF_DET_ARK_JSON: _single_image_annotations_to_det_ark,
        mirpb.AnnoFormat.AF_DET_PASCAL_VOC: _single_image_annotations_to_det_voc,
        mirpb.AnnoFormat.AF_DET_LS_JSON: _single_image_annotations_to_det_ls_json,
        mirpb.AnnoFormat.AF_SEG_POLYGON: _single_image_annotations_to_seg_polygon,
        mirpb.AnnoFormat.AF_SEG_MASK: _single_image_annotations_to_seg_mask,
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


def parse_export_type(type_str: str) -> Tuple["mirpb.AnnoFormat.V", "mirpb.AssetFormat.V"]:
    if not type_str:
        return (mirpb.AnnoFormat.AF_NO_ANNOTATION, mirpb.AssetFormat.AF_RAW)

    anno_str, asset_str = type_str.split(':')
    return (annotations.parse_anno_format(anno_str), parse_asset_format(asset_str))


def get_index_filename(is_asset: Optional[bool] = True,
                       is_pred: Optional[bool] = False,
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


def replace_index_content_inplace(filename: str,
                                  asset_search: str,
                                  asset_replace: str,
                                  anno_search: Optional[str] = None,
                                  anno_replace: Optional[str] = None,
                                  ) -> None:
    if not os.path.isfile(filename):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"index file {filename} not exists.")

    with fileinput.input(filename, inplace=True) as f:
        for line in f:
            if not (anno_search and anno_replace):
                line = line.replace(asset_search, asset_replace)
                continue

            contents = line.strip().split("\t")
            contents[0] = contents[0].replace(asset_search, asset_replace)
            contents[1] = contents[0].replace(anno_search, anno_replace)
            line = "\t".join(contents)


def export_mirdatas_to_dir(
    mir_metadatas: mirpb.MirMetadatas,
    asset_format: "mirpb.AssetFormat.V",
    asset_dir: str,
    media_location: str,
    anno_format: "mirpb.AnnoFormat.V",
    pred_dir: Optional[str] = None,
    gt_dir: Optional[str] = None,
    mir_annotations: Optional[mirpb.MirAnnotations] = None,
    class_ids_mapping: Optional[Dict[int, int]] = None,
    cls_id_mgr: Optional[ClassIdManager] = None,
    tvt_index_dir: Optional[str] = None,
    need_sub_folder: bool = True,
) -> int:
    if asset_format == mirpb.AssetFormat.AF_LMDB:
        return _export_mirdatas_to_lmdb(
            mir_metadatas=mir_metadatas,
            mir_annotations=mir_annotations,
            anno_format=anno_format,
            asset_dir=asset_dir,
            media_location=media_location,
            class_ids_mapping=class_ids_mapping,
            cls_id_mgr=cls_id_mgr,
            tvt_index_dir=tvt_index_dir,
        )
    elif asset_format == mirpb.AssetFormat.AF_RAW:
        return _export_mirdatas_to_raw(
            mir_metadatas=mir_metadatas,
            mir_annotations=mir_annotations,
            anno_format=anno_format,
            asset_dir=asset_dir,
            pred_dir=pred_dir,
            gt_dir=gt_dir,
            media_location=media_location,
            class_ids_mapping=class_ids_mapping,
            cls_id_mgr=cls_id_mgr,
            need_sub_folder=need_sub_folder,
            tvt_index_dir=tvt_index_dir,
        )

    raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message=f"unknown asset format: {asset_format}")


def _export_mirdatas_to_raw(
    mir_metadatas: mirpb.MirMetadatas,
    asset_dir: str,
    media_location: str,
    anno_format: "mirpb.AnnoFormat.V",
    pred_dir: Optional[str] = None,
    gt_dir: Optional[str] = None,
    mir_annotations: Optional[mirpb.MirAnnotations] = None,
    class_ids_mapping: Optional[Dict[int, int]] = None,
    cls_id_mgr: Optional[ClassIdManager] = None,
    tvt_index_dir: Optional[str] = None,
    need_sub_folder: bool = True,
) -> int:
    # Setup.
    if gt_dir:
        os.makedirs(gt_dir, exist_ok=True)
        index_gt_f = open(os.path.join(gt_dir, get_index_filename()), 'w')
    if pred_dir:
        os.makedirs(pred_dir, exist_ok=True)
        index_pred_f = open(os.path.join(pred_dir, get_index_filename()), 'w')

    index_tvt_f: Dict[Tuple[bool, "mirpb.TvtType.V"], TextIO] = {}
    if tvt_index_dir:
        os.makedirs(tvt_index_dir, exist_ok=True)
        for is_pred in [True, False]:
            for tvt_type in [mirpb.TvtType.TvtTypeTraining, mirpb.TvtType.TvtTypeValidation, mirpb.TvtType.TvtTypeTest]:
                file_name = get_index_filename(is_asset=False, is_pred=is_pred, tvt_type=tvt_type)
                index_tvt_f[(is_pred, tvt_type)] = open(os.path.join(tvt_index_dir, file_name), 'w')

    with open(os.path.join(asset_dir, 'index.tsv'), 'w') as index_f:
        for asset_id, attributes in mir_metadatas.attributes.items():
            # export asset.
            asset_src_file: str = mir_storage.locate_asset_path(location=media_location, hash=asset_id)
            asset_dst_path: str = mir_storage.get_asset_storage_path(location=asset_dir,
                                                                     hash=asset_id,
                                                                     need_sub_folder=need_sub_folder)
            asset_ext = _asset_file_ext(attributes.asset_type)
            asset_dst_file = f"{asset_dst_path}.{asset_ext}"
            shutil.copyfile(asset_src_file, asset_dst_file)
            index_f.write(f"{asset_dst_file}\n")

            if anno_format == mirpb.AnnoFormat.AF_NO_ANNOTATION:
                continue

            if (gt_dir and index_gt_f and mir_annotations
                    and asset_id in mir_annotations.ground_truth.image_annotations):
                anno_gt_file = _export_anno_to_file(
                    asset_id=asset_id,
                    anno_format=anno_format,
                    anno_dir=gt_dir,
                    attributes=attributes,
                    image_annotations=mir_annotations.ground_truth.image_annotations[asset_id],
                    image_cks=mir_annotations.image_cks[asset_id],
                    class_ids_mapping=class_ids_mapping,
                    cls_id_mgr=cls_id_mgr,
                    asset_filename=asset_dst_file,
                    need_sub_folder=need_sub_folder,
                )
                asset_anno_pair_line = f"{asset_dst_file}\t{anno_gt_file}\n"
                index_gt_f.write(asset_anno_pair_line)
                if tvt_index_dir:
                    index_tvt_f[(False, attributes.tvt_type)].write(asset_anno_pair_line)

            if (pred_dir and index_pred_f and mir_annotations
                    and asset_id in mir_annotations.prediction.image_annotations):
                anno_pred_file = _export_anno_to_file(
                    asset_id=asset_id,
                    anno_format=anno_format,
                    anno_dir=pred_dir,
                    attributes=attributes,
                    image_annotations=mir_annotations.ground_truth.image_annotations[asset_id],
                    image_cks=None,
                    class_ids_mapping=class_ids_mapping,
                    cls_id_mgr=cls_id_mgr,
                    asset_filename=asset_dst_file,
                    need_sub_folder=need_sub_folder,
                )
                asset_anno_pair_line = f"{asset_dst_file}\t{anno_pred_file}\n"
                index_pred_f.write(asset_anno_pair_line)
                if tvt_index_dir:
                    index_tvt_f[(True, attributes.tvt_type)].write(asset_anno_pair_line)

    # Clean up.
    if gt_dir and index_gt_f:
        index_gt_f.close()
    if pred_dir and index_pred_f:
        index_pred_f.close()
    for index_f in index_tvt_f.values():
        index_f.close()

    return MirCode.RC_OK


def _export_mirdatas_to_lmdb(
    mir_metadatas: mirpb.MirMetadatas,
    asset_dir: str,
    media_location: str,
    anno_format: "mirpb.AnnoFormat.V",
    mir_annotations: Optional[mirpb.MirAnnotations] = None,
    class_ids_mapping: Optional[Dict[int, int]] = None,
    cls_id_mgr: Optional[ClassIdManager] = None,
    tvt_index_dir: Optional[str] = None,
) -> int:
    raise NotImplementedError("LMDB format is not supported yet.")


def _export_anno_to_file(asset_id: str, anno_format: "mirpb.AnnoFormat.V", anno_dir: str,
                         attributes: mirpb.MetadataAttributes, image_annotations: mirpb.SingleImageAnnotations,
                         image_cks: Optional[mirpb.SingleImageCks], class_ids_mapping: Optional[Dict[int, int]],
                         cls_id_mgr: Optional[ClassIdManager], asset_filename: str, need_sub_folder: bool) -> str:
    format_func = _format_file_output_func(anno_format=anno_format)
    anno_str: str = format_func(asset_id=asset_id,
                                attrs=attributes,
                                image_annotations=image_annotations,
                                image_cks=image_cks,
                                class_type_mapping=class_ids_mapping,
                                cls_id_mgr=cls_id_mgr,
                                asset_filename=asset_filename)

    anno_dst_path: str = mir_storage.get_asset_storage_path(location=anno_dir,
                                                            hash=asset_id,
                                                            need_sub_folder=need_sub_folder)
    anno_dst_file = f"{anno_dst_path}.{_anno_file_ext(anno_format=anno_format)}"
    with open(anno_dst_file, 'w') as af:
        af.write(anno_str)
    return anno_dst_file


def _single_image_annotations_to_det_ark(attributes: mirpb.MetadataAttributes,
                                         image_annotations: mirpb.SingleImageAnnotations,
                                         image_cks: Optional[mirpb.SingleImageCks],
                                         class_ids_mapping: Optional[Dict[int, int]], cls_id_mgr: ClassIdManager,
                                         asset_filename: str) -> str:
    output_str = ""
    for annotation in image_annotations.boxes:
        mapped_id = class_ids_mapping[annotation.class_id] if class_ids_mapping else annotation.class_id
        output_str += f"{mapped_id}, {annotation.box.x}, {annotation.box.y}, "
        output_str += f"{annotation.box.x + annotation.box.w - 1}, {annotation.box.y + annotation.box.h - 1}, "
        output_str += f"{annotation.anno_quality}, {annotation.box.rotate_angle}\n"
    return output_str


def _single_image_annotations_to_det_voc(attributes: mirpb.MetadataAttributes,
                                         image_annotations: mirpb.SingleImageAnnotations,
                                         image_cks: Optional[mirpb.SingleImageCks],
                                         class_ids_mapping: Optional[Dict[int, int]], cls_id_mgr: ClassIdManager,
                                         asset_filename: str) -> str:
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
        object_node = ElementTree.SubElement(annotation_node, 'object')

        name_node = ElementTree.SubElement(object_node, 'name')
        name_node.text = cls_id_mgr.main_name_for_id(annotation.class_id) or 'unknown'

        pose_node = ElementTree.SubElement(object_node, 'pose')
        pose_node.text = 'unknown'

        truncated_node = ElementTree.SubElement(object_node, 'truncated')
        truncated_node.text = 'unknown'

        occluded_node = ElementTree.SubElement(object_node, 'occluded')
        occluded_node.text = '0'

        bndbox_node = ElementTree.SubElement(object_node, 'bndbox')

        xmin_node = ElementTree.SubElement(bndbox_node, 'xmin')
        xmin_node.text = str(annotation.box.x)

        ymin_node = ElementTree.SubElement(bndbox_node, 'ymin')
        ymin_node.text = str(annotation.box.y)

        xmax_node = ElementTree.SubElement(bndbox_node, 'xmax')
        xmax_node.text = str(annotation.box.x + annotation.box.w - 1)

        ymax_node = ElementTree.SubElement(bndbox_node, 'ymax')
        ymax_node.text = str(annotation.box.y + annotation.box.h - 1)

        rotate_angle_node = ElementTree.SubElement(bndbox_node, 'rotate_angle')
        rotate_angle_node.text = f"{annotation.box.rotate_angle:.4f}"

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

    return ElementTree.tostring(element=annotation_node, encoding='unicode')


def _single_image_annotations_to_det_ls_json(attributes: mirpb.MetadataAttributes,
                                             image_annotations: mirpb.SingleImageAnnotations,
                                             image_cks: Optional[mirpb.SingleImageCks],
                                             class_ids_mapping: Optional[Dict[int, int]], cls_id_mgr: ClassIdManager,
                                             asset_filename: str) -> str:
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
        bbox_x, bbox_y = float(annotation.box.x), float(annotation.box.y)
        bbox_width, bbox_height = float(annotation.box.w), float(annotation.box.h)
        img_width, img_height = attributes.width, attributes.height
        item = {
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
                "rectanglelabels": [cls_id_mgr.main_name_for_id(annotation.class_id) or 'unknown']
            },
            "to_name": to_name,
            "from_name": from_name,
            "image_rotation": 0,
            "original_width": img_width,
            "original_height": img_height
        }
        task[out_type][0]['result'].append(item)
    return json.dumps(task)


def _single_image_annotations_to_seg_polygon(attributes: mirpb.MetadataAttributes,
                                             image_annotations: mirpb.SingleImageAnnotations,
                                             image_cks: Optional[mirpb.SingleImageCks],
                                             class_ids_mapping: Optional[Dict[int, int]], cls_id_mgr: ClassIdManager,
                                             asset_filename: str) -> str:
    raise NotImplementedError("seg exporter not implemented")


def _single_image_annotations_to_seg_mask(attributes: mirpb.MetadataAttributes,
                                          image_annotations: mirpb.SingleImageAnnotations,
                                          image_cks: Optional[mirpb.SingleImageCks],
                                          class_ids_mapping: Optional[Dict[int, int]], cls_id_mgr: ClassIdManager,
                                          asset_filename: str) -> str:
    raise NotImplementedError("seg exporter not implemented")

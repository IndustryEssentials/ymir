from enum import Enum
import json
import os
import shutil
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import uuid
import xml.etree.ElementTree as ElementTree

import lmdb
from PIL import Image, UnidentifiedImageError

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import class_ids, data_reader
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


class AssetFormat(str, Enum):
    ASSET_FORMAT_UNKNOWN = 'unknown'
    ASSET_FORMAT_RAW = 'raw'
    ASSET_FORMAT_LMDB = 'lmdb'


class AnnoFormat(str, Enum):
    ANNO_FORMAT_UNKNOWN = 'unknown'
    ANNO_FORMAT_NO_ANNOTATION = 'none'
    ANNO_FORMAT_ARK = 'ark'
    ANNO_FORMAT_VOC = 'voc'
    ANNO_FORMAT_LS_JSON = 'ls_json'  # label studio json format


def check_support_format(anno_format: str) -> bool:
    return anno_format in support_format_type()


def support_format_type() -> List[str]:
    return [f.value for f in AnnoFormat]


def support_asset_format_type() -> List[str]:
    return [f.value for f in AssetFormat]


def format_type_from_str(anno_format: str) -> AnnoFormat:
    return AnnoFormat(anno_format.lower())


def asset_format_type_from_str(asset_format: str) -> AssetFormat:
    return AssetFormat(asset_format.lower())


def get_export_type(type_str: str) -> Tuple[AnnoFormat, AssetFormat]:
    if not type_str:
        return (AnnoFormat.ANNO_FORMAT_ARK, AssetFormat.ASSET_FORMAT_RAW)

    ef, af = type_str.split(':')
    return (AnnoFormat(ef), AssetFormat(af))


def _format_file_output_func(anno_format: AnnoFormat) -> Callable:
    _format_func_map = {
        AnnoFormat.ANNO_FORMAT_ARK: _single_image_annotations_to_ark,
        AnnoFormat.ANNO_FORMAT_VOC: _single_image_annotations_to_voc,
        AnnoFormat.ANNO_FORMAT_LS_JSON: _single_image_annotations_to_ls_json,
    }
    return _format_func_map[anno_format]


def _format_file_ext(anno_format: AnnoFormat) -> str:
    _format_ext_map = {
        AnnoFormat.ANNO_FORMAT_ARK: '.txt',
        AnnoFormat.ANNO_FORMAT_VOC: '.xml',
        AnnoFormat.ANNO_FORMAT_LS_JSON: '.json',
    }
    return _format_ext_map[anno_format]


def _single_image_annotations_to_ark(asset_id: str, attrs: mirpb.MetadataAttributes,
                                     image_annotations: mirpb.SingleImageAnnotations,
                                     class_type_mapping: Optional[Dict[int, int]], cls_id_mgr: class_ids.ClassIdManager,
                                     asset_filename: str) -> str:
    output_str = ""
    for annotation in image_annotations.annotations:
        mapped_id = class_type_mapping[annotation.class_id] if class_type_mapping else annotation.class_id
        output_str += f"{mapped_id}, {annotation.box.x}, {annotation.box.y}, "
        output_str += f"{annotation.box.x + annotation.box.w - 1}, {annotation.box.y + annotation.box.h - 1}\n"
    return output_str


def _single_image_annotations_to_voc(asset_id: str, attrs: mirpb.MetadataAttributes,
                                     image_annotations: mirpb.SingleImageAnnotations,
                                     class_type_mapping: Optional[Dict[int, int]], cls_id_mgr: class_ids.ClassIdManager,
                                     asset_filename: str) -> str:
    annotations = image_annotations.annotations

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

    # annotation: source: database
    database_node = ElementTree.SubElement(source_node, 'database')
    database_node.text = attrs.dataset_name or 'unknown'

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
    width_node.text = str(attrs.width)

    # annotation: size: height
    height_node = ElementTree.SubElement(size_node, 'height')
    height_node.text = str(attrs.height)

    # annotation: size: depth
    depth_node = ElementTree.SubElement(size_node, 'depth')
    depth_node.text = str(attrs.image_channels)

    # annotation: segmented
    segmented_node = ElementTree.SubElement(annotation_node, 'segmented')
    segmented_node.text = '0'

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

        difficult_node = ElementTree.SubElement(object_node, 'difficult')
        difficult_node.text = '0'

    return ElementTree.tostring(element=annotation_node, encoding='unicode')


def _single_image_annotations_to_ls_json(asset_id: str, attrs: mirpb.MetadataAttributes,
                                         image_annotations: mirpb.SingleImageAnnotations,
                                         class_type_mapping: Optional[Dict[int, int]],
                                         cls_id_mgr: class_ids.ClassIdManager, asset_filename: str) -> str:
    annotations = image_annotations.annotations

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
        img_width, img_height = attrs.width, attrs.height
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


class BaseDataWriter:
    def __init__(self, mir_root: str, assets_location: str, class_ids_mapping: Dict[int, int],
                 format_type: AnnoFormat) -> None:
        if not assets_location:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty assets_location')

        self._class_id_manager = class_ids.ClassIdManager(mir_root=mir_root)
        self._assets_location = assets_location
        self._class_ids_mapping = class_ids_mapping
        self._format_type = format_type

    def _write(self, asset_id: str, attrs: mirpb.MetadataAttributes,
               image_annotations: mirpb.SingleImageAnnotations) -> None:
        """
        write assets and annotations to destination with proper format

        Args:
            asset_id (str): asset hash code
            attrs (mirpb.MetadataAttributes): attributes to this asset
            image_annotations (mirpb.SingleImageAnnotations): annotations to this asset
        """
        raise NotImplementedError('not implemented')

    def _close(self) -> None:
        """
        close writer
        """
        raise NotImplementedError('not implemented')

    def write_all(self, dr: data_reader.MirDataReader) -> None:
        """
        write all datas from data reader
        """
        raise NotImplementedError('not implemented')


class RawDataWriter(BaseDataWriter):
    def __init__(self,
                 mir_root: str,
                 assets_location: str,
                 assets_dir: str,
                 annotations_dir: str,
                 need_ext: bool,
                 need_id_sub_folder: bool,
                 overwrite: bool,
                 class_ids_mapping: Dict[int, int],
                 format_type: AnnoFormat,
                 index_file_path: str = '',
                 index_assets_prefix: str = '',
                 index_annotations_prefix: str = '') -> None:
        """
        Args:
            assets_location (str): path to assets storage directory
            assets_dir (str): export asset directory
            annotations_dir (str): export annotation directory, if format_type is NO_ANNOTATION, this could be None
            need_ext (bool): if true, all export assets will have it's type as ext, jpg, png, etc.
            need_id_sub_folder (bool): if True, use last 2 chars of asset id as a sub folder name
            format_type (AnnoFormat): format type, NONE means exports no annotations
            overwrite (bool): if true, export assets even if they are exist in destination position
            class_ids_mapping (Dict[int, int]): key: ymir class id, value: class id in exported annotation files
            index_file_path (str): path to index file, if None, generates no index file
            index_assets_prefix (str): prefix path added to each asset index path
            index_annotations_prefix (str): prefix path added to each annotation index path
        """
        super().__init__(mir_root=mir_root,
                         assets_location=assets_location,
                         class_ids_mapping=class_ids_mapping,
                         format_type=format_type)

        # prepare out dirs
        os.makedirs(assets_dir, exist_ok=True)
        if annotations_dir:
            os.makedirs(annotations_dir, exist_ok=True)
        if index_file_path:
            os.makedirs(os.path.dirname(index_file_path), exist_ok=True)

        self._assets_dir = assets_dir
        self._annotations_dir = annotations_dir
        self._need_ext = need_ext
        self._need_id_sub_folder = need_id_sub_folder
        self._format_type = format_type
        self._index_file = open(index_file_path, 'w') if index_file_path else None
        self._index_assets_prefix = index_assets_prefix
        self._index_annotations_prefix = index_annotations_prefix
        self._overwrite = overwrite

    def _write(self, asset_id: str, attrs: mirpb.MetadataAttributes,
               image_annotations: mirpb.SingleImageAnnotations) -> None:
        # write asset
        asset_src_path = os.path.join(self._assets_location, asset_id)
        sub_folder_name = asset_id[-2:] if self._need_id_sub_folder else ''

        asset_file_name = asset_id
        if self._need_ext:
            try:
                asset_image = Image.open(asset_src_path)
                asset_file_name = f"{asset_file_name}.{asset_image.format.lower()}"  # type: ignore
            except UnidentifiedImageError:
                asset_file_name = f"{asset_file_name}.unknown"

        asset_dest_dir = os.path.join(self._assets_dir, sub_folder_name)
        os.makedirs(asset_dest_dir, exist_ok=True)
        asset_dest_path = os.path.join(asset_dest_dir, asset_file_name)
        if self._overwrite or not os.path.isfile(asset_dest_path):
            shutil.copyfile(asset_src_path, asset_dest_path)

        # write annotations
        anno_file_name = ''
        if self._format_type != AnnoFormat.ANNO_FORMAT_NO_ANNOTATION:
            format_func = _format_file_output_func(anno_format=self._format_type)
            anno_str: str = format_func(asset_id=asset_id,
                                        attrs=attrs,
                                        image_annotations=image_annotations,
                                        class_type_mapping=self._class_ids_mapping,
                                        cls_id_mgr=self._class_id_manager,
                                        asset_filename=asset_file_name)

            anno_dest_dir = os.path.join(self._annotations_dir, sub_folder_name)
            os.makedirs(anno_dest_dir, exist_ok=True)
            anno_file_name = f"{asset_id}{_format_file_ext(self._format_type)}"
            anno_dest_path = os.path.join(anno_dest_dir, anno_file_name)
            with open(anno_dest_path, 'w') as f:
                f.write(anno_str)

        # write index file
        if self._index_file:
            asset_path_in_index_file = os.path.join(self._index_assets_prefix, sub_folder_name, asset_file_name)
            if self._format_type != AnnoFormat.ANNO_FORMAT_NO_ANNOTATION:
                anno_path_in_index_file = os.path.join(self._index_annotations_prefix, sub_folder_name, anno_file_name)
                self._index_file.write(f"{asset_path_in_index_file}\t{anno_path_in_index_file}\n")
            else:
                self._index_file.write(f"{asset_path_in_index_file}\n")

    def _close(self) -> None:
        if not self._index_file:
            return

        self._index_file.close()
        self._index_file = None

    def write_all(self, dr: data_reader.MirDataReader) -> None:
        for v in dr.read():
            self._write(*v)
        self._close()


class LmdbDataWriter(BaseDataWriter):
    def __init__(self,
                 mir_root: str,
                 assets_location: str,
                 lmdb_dir: str,
                 class_ids_mapping: Dict[int, int],
                 format_type: AnnoFormat,
                 index_file_path: str = '') -> None:
        super().__init__(mir_root=mir_root,
                         assets_location=assets_location,
                         class_ids_mapping=class_ids_mapping,
                         format_type=format_type)

        if not lmdb_dir:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty assets_dir or lmdb_dir')

        # prepare out dirs
        os.makedirs(lmdb_dir, exist_ok=True)
        if index_file_path:
            os.makedirs(os.path.dirname(index_file_path), exist_ok=True)

        self._lmdb_dir = lmdb_dir
        self._index_file_path = index_file_path
        self._finish_file_path = os.path.join(self._lmdb_dir, '.finish')
        self._lmdb_env: Any  # see write_all
        self._lmdb_tnx: Any
        self._lmdb_index: Any

    def exists(self) -> bool:
        data_exists = os.path.isfile(os.path.join(self._lmdb_dir, 'data.mdb'))
        lock_exists = os.path.isfile(os.path.join(self._lmdb_dir, 'lock.mdb'))
        if not data_exists or not lock_exists:
            return False

        counter = 0
        while not os.path.isfile(self._finish_file_path):
            time.sleep(30)
            counter += 1
            if counter >= 3:
                raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                      error_message='lmdb writer: others are writing')
        return True

    def _write(self, asset_id: str, attrs: mirpb.MetadataAttributes,
               image_annotations: mirpb.SingleImageAnnotations) -> None:
        # read asset
        asset_src_path = os.path.join(self._assets_location, asset_id)
        with open(asset_src_path, 'rb') as f:
            asset_data = f.read()

        # write asset and annotations
        anno_key_name = ''
        if self._format_type != AnnoFormat.ANNO_FORMAT_NO_ANNOTATION:
            format_func = _format_file_output_func(anno_format=self._format_type)
            anno_data: bytes = format_func(asset_id=asset_id,
                                           attrs=attrs,
                                           image_annotations=image_annotations,
                                           class_type_mapping=self._class_ids_mapping,
                                           cls_id_mgr=self._class_id_manager,
                                           asset_filename='').encode()

            asset_key_name = f"asset_{asset_id}"
            anno_key_name = f"anno_{asset_id}"
            self._lmdb_tnx.put(asset_key_name.encode(), asset_data)
            self._lmdb_tnx.put(anno_key_name.encode(), anno_data)

        # write index file
        if self._lmdb_index:
            if self._format_type != AnnoFormat.ANNO_FORMAT_NO_ANNOTATION:
                self._lmdb_index.write(f"{asset_key_name}\t{anno_key_name}\n")
            else:
                self._lmdb_index.write(f"{asset_key_name}\n")

    def _close(self) -> None:
        if self._lmdb_env:
            self._lmdb_tnx.commit()
            self._lmdb_tnx = None
            self._lmdb_env.close()
            self._lmdb_env = None
        if self._lmdb_index:
            self._lmdb_index.close()
            self._lmdb_index = None
        if self._index_file_path:
            shutil.copyfile(src=os.path.join(self._lmdb_dir, 'index.mdb'), dst=self._index_file_path)

    def write_all(self, dr: data_reader.MirDataReader) -> None:
        # if already exists, no need to write, only copy index file to destination
        if self.exists():
            if self._index_file_path:
                shutil.copyfile(src=os.path.join(self._lmdb_dir, 'index.mdb'), dst=self._index_file_path)
            return

        # write all
        self._lmdb_env = lmdb.open(self._lmdb_dir, map_size=1099511627776)  # 1TB
        self._lmdb_tnx = self._lmdb_env.begin(write=True)
        self._lmdb_index = open(os.path.join(self._lmdb_dir, 'index.mdb'), 'w')
        for v in dr.read():
            self._write(*v)
        self._close()
        # touch a finish file
        open(self._finish_file_path, 'w').close()

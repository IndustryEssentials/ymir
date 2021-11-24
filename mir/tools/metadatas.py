import logging
import os
import time
from PIL import Image, ImageFile, UnidentifiedImageError
from typing import Tuple

from mir.tools.code import MirCode
from mir.tools.phase_logger import PhaseLoggerCenter, PhaseStateEnum
from mir.protos import mir_command_pb2 as mirpb

ImageFile.LOAD_TRUNCATED_IMAGES = True


def _generate_metadata_mir_pb(mir_metadatas: mirpb.MirMetadatas, dataset_name: str, sha1s: list,
                              hashed_asset_root: str, phase: str) -> int:
    """
    generate mirpb.MirMetadatas from sha1s
    """
    current_timestamp = int(time.time())  # this is a fake timestamp
    timestamp = mirpb.Timestamp()
    timestamp.start = current_timestamp
    timestamp.duration = 0  # image has no duraton

    unknown_format_count = 0

    sha1s_count = len(sha1s)
    for idx, val in enumerate(sha1s):
        metadata_attributes = mirpb.MetadataAttributes()
        metadata_attributes.timestamp.CopyFrom(timestamp)
        metadata_attributes.dataset_name = dataset_name

        # read file
        # if any exception occured, exit without any handler
        hashed_asset_path = os.path.join(hashed_asset_root, val)
        asset_type, width, height, channel = _type_shape_for_asset(hashed_asset_path)
        if asset_type == mirpb.AssetTypeUnknown:
            logging.warning(f"ignore asset with unknown format, id: {val}")
            unknown_format_count += 1
            continue
        metadata_attributes.asset_type = asset_type
        metadata_attributes.width = width
        metadata_attributes.height = height
        metadata_attributes.image_channels = channel

        mir_metadatas.attributes[val].CopyFrom(metadata_attributes)

        if idx > 0 and idx % 5000 == 0:
            PhaseLoggerCenter.update_phase(phase=phase, local_percent=(idx / sha1s_count))

    if unknown_format_count > 0:
        logging.warning(f"unknown format asset count: {unknown_format_count}")

    return MirCode.RC_OK


_ASSET_TYPE_STR_TO_ENUM_MAPPING = {
    'jpeg': mirpb.AssetTypeImageJpeg,
    'jpg': mirpb.AssetTypeImageJpeg,
    'png': mirpb.AssetTypeImagePng,
    'bmp': mirpb.AssetTypeImageBmp,
}


def _type_shape_for_asset(asset_path: str) -> Tuple['mirpb.AssetType.V', int, int, int]:
    if not asset_path:
        raise ValueError('_type_shape_for_asset: empty asset_path')

    try:
        asset_image = Image.open(asset_path)
        asset_type_str: str = asset_image.format.lower()
    except UnidentifiedImageError as e:
        asset_type_str = ''  # didn't set it to 'unknown' as what i did in utils.py, because this is easy to compare

    if asset_type_str in _ASSET_TYPE_STR_TO_ENUM_MAPPING:
        width, height = asset_image.size
        channel = len(asset_image.getbands())
        return (_ASSET_TYPE_STR_TO_ENUM_MAPPING[asset_type_str], width, height, channel)
    else:
        return (mirpb.AssetTypeUnknown, 0, 0, 0)


def import_metadatas(mir_metadatas: mirpb.MirMetadatas, dataset_name: str, in_sha1_path: str, hashed_asset_root: str,
                     phase: str = '') -> int:
    # if not enough args, abort
    if (not in_sha1_path or not dataset_name or not hashed_asset_root):
        logging.error('invalid in_sha1_path, dataset_name or hashed_asset_root')
        return MirCode.RC_CMD_INVALID_ARGS

    if not mir_metadatas:
        # some errors occured, show error message
        logging.error('mir_metadatas empty')
        return MirCode.RC_CMD_INVALID_MIR_REPO

    # read sha1
    sha1s = []
    with open(in_sha1_path, "r") as in_file:
        for line in in_file.readlines():
            if not line or not line.strip():
                continue
            line_components = line.strip().split()
            if not line_components[0]:
                continue
            sha1s.append(line_components[0])
    if not sha1s:
        logging.error(f"no sha1s found in {in_sha1_path}, exit")
        return MirCode.RC_CMD_INVALID_ARGS

    # generate mir_metadatas
    ret = _generate_metadata_mir_pb(mir_metadatas=mir_metadatas,
                                    dataset_name=dataset_name,
                                    sha1s=sha1s,
                                    hashed_asset_root=hashed_asset_root,
                                    phase=phase)
    return ret

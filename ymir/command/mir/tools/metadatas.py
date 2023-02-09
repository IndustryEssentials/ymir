import logging
import os
import time
from PIL import Image, ImageFile, UnidentifiedImageError
from typing import Dict
from mir.tools import mir_storage

from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.tools.phase_logger import PhaseLoggerCenter
from mir.protos import mir_command_pb2 as mirpb

ImageFile.LOAD_TRUNCATED_IMAGES = True


_ASSET_TYPE_STR_TO_ENUM_MAPPING = {
    'jpeg': mirpb.AssetTypeImageJpeg,
    'jpg': mirpb.AssetTypeImageJpeg,
    'png': mirpb.AssetTypeImagePng,
    'bmp': mirpb.AssetTypeImageBmp,
}


def _fill_type_shape_size_for_asset(asset_path: str, metadata_attributes: mirpb.MetadataAttributes) -> None:
    if not asset_path:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='_type_shape_size_for_asset: empty asset_path')

    try:
        asset_image = Image.open(asset_path)
        asset_type_str: str = asset_image.format.lower()  # type: ignore
    except (UnidentifiedImageError, OSError) as e:
        logging.info(f"{type(e).__name__}: {e} asset_path: {asset_path}")
        asset_type_str = ''  # didn't set it to 'unknown' as what i did in utils.py, because this is easy to compare

    width, height, channel = 0, 0, 0
    asset_type = mirpb.AssetTypeUnknown
    if asset_type_str in _ASSET_TYPE_STR_TO_ENUM_MAPPING:
        width, height = asset_image.size
        channel = len(asset_image.getbands())
        asset_type = _ASSET_TYPE_STR_TO_ENUM_MAPPING[asset_type_str]

    metadata_attributes.asset_type = asset_type
    metadata_attributes.width = width
    metadata_attributes.height = height
    metadata_attributes.image_channels = channel
    metadata_attributes.byte_size = os.stat(asset_path).st_size


def import_metadatas(mir_metadatas: mirpb.MirMetadatas,
                     file_name_to_asset_ids: Dict[str, str],
                     hashed_asset_root: str,
                     phase: str = '') -> int:
    # if not enough args, abort
    if (not file_name_to_asset_ids or not hashed_asset_root):
        logging.error('invalid map_hashed_path or hashed_asset_root')
        return MirCode.RC_CMD_INVALID_ARGS

    if not mir_metadatas:
        # some errors occured, show error message
        logging.error('mir_metadatas empty')
        return MirCode.RC_CMD_INVALID_MIR_REPO

    current_timestamp = int(time.time())  # this is a fake timestamp
    timestamp = mirpb.Timestamp()
    timestamp.start = current_timestamp
    timestamp.duration = 0  # image has no duraton

    unknown_format_count = 0
    zero_size_count = 0

    sha1s_count = len(file_name_to_asset_ids)
    for idx, (file_name, asset_id) in enumerate(file_name_to_asset_ids.items()):
        metadata_attributes = mirpb.MetadataAttributes()
        metadata_attributes.timestamp.CopyFrom(timestamp)

        # read file
        # if any exception occured, exit without any handler
        hashed_asset_path = mir_storage.locate_asset_path(location=hashed_asset_root, hash=asset_id)
        _fill_type_shape_size_for_asset(hashed_asset_path, metadata_attributes)
        if metadata_attributes.asset_type == mirpb.AssetTypeUnknown:
            unknown_format_count += 1
            continue
        if metadata_attributes.width <= 0 or metadata_attributes.height <= 0:
            zero_size_count += 1
            continue

        metadata_attributes.origin_filename = file_name
        mir_metadatas.attributes[asset_id].CopyFrom(metadata_attributes)

        if idx > 0 and idx % 5000 == 0:
            PhaseLoggerCenter.update_phase(phase=phase, local_percent=(idx / sha1s_count))

    logging.info(f"count of unknown format assets: {unknown_format_count}")
    logging.info(f"count of zero size assets: {zero_size_count}")

    return MirCode.RC_OK

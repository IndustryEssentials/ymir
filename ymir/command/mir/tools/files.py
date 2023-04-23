import os
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import requests
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    Timeout,
)

from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


def _locate_dir(p: Path, targets: List[str]) -> Path:
    """
    Locate specifc target dirs
    """
    for _p in p.iterdir():
        if not _p.is_dir():
            continue
        if _p.name.lower() in targets:
            return _p
        for __p in _p.iterdir():
            if not __p.is_dir():
                continue
            if __p.name.lower() in targets:
                return __p
    # Only search 3rd depth when no result was found in 2nd depth.
    for _p in p.iterdir():
        if not _p.is_dir():
            continue
        for __p in _p.iterdir():
            if not __p.is_dir():
                continue
            for ___p in __p.iterdir():
                if ___p.is_dir() and ___p.name.lower() in targets:
                    return ___p
    raise FileNotFoundError


def _locate_annotation_dir(p: Path, targets: List[str]) -> Optional[Path]:
    """
    annotation_dir (gt or pred) must be in sibling with asset_dir
    p: asset_dir.parent
    targets: ["Annotations", "gt"] or ["pred"]
    """
    for _p in Path(p).iterdir():
        if not _p.is_dir():
            continue
        if _p.name.lower() in targets:
            return _p
    return None


def locate_ymir_dataset_dirs(dataset_root_dir: str) -> Tuple[str, Optional[str]]:
    # only `asset_dir` (images) is required
    # both `gt_dir` and `pred_dir` are optional
    asset_dir = _locate_dir(Path(dataset_root_dir), ["images", "jpegimages"])
    gt_dir = _locate_annotation_dir(asset_dir.parent, ["gt", "annotations"])
    return str(asset_dir), str(gt_dir) if gt_dir else None


def download_file(
    url: str,
    output_dir: str,
) -> str:
    try:
        resp = requests.get(url, timeout=5, verify=False)
        if resp.status_code == requests.codes.not_found:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE,
                                  error_message=f"Failed to download: {url}, status code: {resp.status_code}")
    except (
        ConnectionError,
        HTTPError,
        MissingSchema,
        InvalidSchema,
        InvalidURL,
        Timeout,
    ) as e:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE,
                              error_message=f"Failed to download: {url}, error: {e}")

    output_file = os.path.join(output_dir, os.path.basename(urlparse(url).path))
    with open(output_file, "wb") as f:
        for chunk in resp.iter_content(1024):
            f.write(chunk)
    return output_file

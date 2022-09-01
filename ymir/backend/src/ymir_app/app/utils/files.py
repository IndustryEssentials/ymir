import hashlib
import logging
import os
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from tempfile import NamedTemporaryFile, mkdtemp
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse

import requests
from fastapi.logger import logger
from pydantic import AnyHttpUrl
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    Timeout,
)

from app.config import settings

env = os.environ.get

BUF_SIZE = 65536

NGINX_DATA_PATH = env("NGINX_DATA_PATH", "./")
NGINX_PREFIX = env("NGINX_PREFIX", "")
MAX_WORKERS = int(env("MAX_WORKERS", 5))
DOWNLOAD_TIMEOUT = int(env("DOWNLOAD_TIMEOUT", 10))


class FailedToDownload(Exception):
    pass


class InvalidFileStructure(Exception):
    pass


def md5_of_file(file: Any) -> str:
    md5 = hashlib.md5()
    file.seek(0)
    while True:
        data = file.read(BUF_SIZE)
        if not data:
            break
        md5.update(data)
    file.seek(0)
    return md5.hexdigest()


def host_file(file: Any) -> str:
    p = Path(file.filename)
    target = (Path(NGINX_DATA_PATH) / md5_of_file(file.file)).with_suffix(p.suffix)
    with open(target, "wb") as f:
        f.write(file.file.read())
    return urljoin(NGINX_PREFIX, str(target))


def save_file_content(url: Union[AnyHttpUrl, str], output_filename: Union[Path, str]) -> None:
    if urlparse(url).netloc:
        return download_file(url, output_filename)  # type: ignore

    # if file is hosted by nginx on the same host, just copy it
    file_path = Path(NGINX_DATA_PATH) / url
    shutil.move(str(file_path), output_filename)


def download_file(url: AnyHttpUrl, output_filename: str) -> None:
    try:
        resp = requests.get(url, timeout=5, verify=False)
        if resp.status_code == requests.codes.not_found:
            raise FailedToDownload(url)
    except (
        ConnectionError,
        HTTPError,
        MissingSchema,
        InvalidSchema,
        InvalidURL,
        Timeout,
    ):
        raise FailedToDownload(url)
    with open(output_filename, "wb") as f:
        for chunk in resp.iter_content(1024):
            f.write(chunk)


def decompress_zip(zip_file_path: Union[str, Path], output_dir: Union[str, Path]) -> None:
    with zipfile.ZipFile(str(zip_file_path), "r") as zip_ref:
        zip_ref.extractall(str(output_dir))


def save_file(
    url: Union[AnyHttpUrl, str],
    output_dir: Union[str, Path],
    output_filename: Optional[str] = None,
) -> Path:
    filename = output_filename or Path(urlparse(url).path).name
    output_file = Path(output_dir) / filename
    save_file_content(url, output_file)
    return output_file


def save_files(urls: List[Union[AnyHttpUrl, str]], output_basedir: Union[str, Path]) -> Tuple[str, Dict]:
    output_dir = mkdtemp(prefix="import_files_", dir=output_basedir)
    save_ = partial(save_file, output_dir=Path(output_dir))
    workers = min(MAX_WORKERS, len(urls))
    with ThreadPoolExecutor(workers) as executor:
        res = executor.map(save_, urls)
    return output_dir, {filename.name: url for filename, url in zip(res, urls)}


def locate_dir(p: Union[str, Path], targets: List[str]) -> Path:
    """
    Locate specifc target dirs
    """
    for _p in Path(p).iterdir():
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
    for _p in Path(p).iterdir():
        if not _p.is_dir():
            continue
        for __p in _p.iterdir():
            if not __p.is_dir():
                continue
            for ___p in __p.iterdir():
                if ___p.is_dir() and ___p.name.lower() in targets:
                    return ___p
    raise FileNotFoundError


def locate_annotation_dir(p: Path, targets: List[str]) -> Optional[Path]:
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


def locate_ymir_dataset_dirs(path: Path) -> Tuple[Path, Optional[Path], Optional[Path]]:
    # only `asset_dir` (images) is required
    # both `gt_dir` and `pred_dir` are optional
    asset_dir = locate_dir(path, ["images", "jpegimages"])
    gt_dir = locate_annotation_dir(asset_dir.parent, ["gt", "annotations"])
    pred_dir = locate_annotation_dir(asset_dir.parent, ["pred"])
    return asset_dir, gt_dir, pred_dir


def prepare_downloaded_paths(url: str, output_dir: Union[str, Path]) -> Tuple[Path, Optional[Path], Optional[Path]]:
    with NamedTemporaryFile("wb") as tmp:
        save_file_content(url, tmp.name)
        logging.info("[import dataset] url content cached to %s", tmp.name)
        decompress_zip(tmp.name, output_dir)

    return locate_ymir_dataset_dirs(output_dir)


def is_relative_to(path_long: Union[str, Path], path_short: Union[str, Path]) -> bool:
    """
    mimic the behavior of Path.is_relative_to in Python 3.9
    for example, /x/y/z is relative to /x/
    """
    return Path(path_short) in Path(path_long).parents


def locate_import_paths(src_path: Union[str, Path]) -> Tuple[Path, Optional[Path], Optional[Path]]:
    asset_dir, gt_dir, pred_dir = locate_ymir_dataset_dirs(Path(src_path))

    if not is_relative_to(asset_dir, settings.SHARED_DATA_DIR):
        logger.error("import path (%s) not within shared_dir (%s)" % (asset_dir, settings.SHARED_DATA_DIR))
        raise InvalidFileStructure()
    return asset_dir, gt_dir, pred_dir

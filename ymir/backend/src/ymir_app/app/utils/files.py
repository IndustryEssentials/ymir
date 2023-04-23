import hashlib
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from tempfile import mkdtemp
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse

import requests
from pydantic import AnyHttpUrl
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    Timeout,
)


env = os.environ.get

BUF_SIZE = 65536

NGINX_DATA_PATH = env("NGINX_DATA_PATH", "./")
NGINX_PREFIX = env("NGINX_PREFIX", "")
MAX_WORKERS = int(env("MAX_WORKERS", 5))


class FailedToDownload(Exception):
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


def save_file_content(url: Union[AnyHttpUrl, str], output_filename: Union[Path, str], keep: bool = False) -> None:
    if urlparse(url).netloc:
        return download_file(url, output_filename)  # type: ignore

    # if file is hosted by nginx on the same host, just copy it
    file_path = Path(NGINX_DATA_PATH) / url
    if keep:
        shutil.copy(str(file_path), output_filename)
    else:
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


def save_file(
    url: Union[AnyHttpUrl, str],
    output_dir: Union[str, Path],
    output_filename: Optional[str] = None,
    keep: bool = False,
) -> Path:
    filename = output_filename or Path(urlparse(url).path).name
    output_file = Path(output_dir) / filename
    save_file_content(url, output_file, keep)
    return output_file


def save_files(
    urls: List[Union[AnyHttpUrl, str]], output_basedir: Union[str, Path], keep: bool = False
) -> Tuple[str, Dict]:
    output_dir = mkdtemp(prefix="import_files_", dir=output_basedir)
    save_ = partial(save_file, output_dir=Path(output_dir), keep=keep)
    workers = min(MAX_WORKERS, len(urls))
    with ThreadPoolExecutor(workers) as executor:
        res = executor.map(save_, urls)
    return output_dir, {filename.name: url for filename, url in zip(res, urls)}

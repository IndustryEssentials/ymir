
import logging

from common_utils.sandbox import SandboxInfo


def update_all(sandbox_info: SandboxInfo) -> None:
    logging.info('1.1.0 -> 1.3.0')
    logging.info(f"sandbox root: {sandbox_info.root}")

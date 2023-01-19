import logging
import errno
from typing import Optional

from app.config import settings
from app.utils.ymir_controller import ControllerClient
from common_utils.version import YMIR_REPO_VERSION, ymir_salient_version

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_msg_box(msg: str, indent: int = 1, width: Optional[int] = None, title: Optional[str] = None) -> str:
    """https://stackoverflow.com/a/58780542/2888638"""
    lines = msg.split("\n")
    space = " " * indent
    if not width:
        width = max(map(len, lines))
    box = f'\n╔{"═" * (width + indent * 2)}╗\n'
    if title:
        box += f"║{space}{title:<{width}}{space}║\n"
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'
    box += "".join([f"║{space}{line:<{width}}{space}║\n" for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'
    return box


def check_mir_repo_version() -> None:
    controller = ControllerClient(settings.GRPC_CHANNEL)
    try:
        sandbox_versions = controller.get_cmd_version()
    except ValueError:
        logger.exception("[start up] Failed to get mir repo version")
        raise
    if not sandbox_versions:
        # no versions found, fresh workplace.
        return
    if len(sandbox_versions) > 1:
        raise ValueError(f"multiple versions detected: {sandbox_versions}")
    if ymir_salient_version(sandbox_versions[0]) != YMIR_REPO_VERSION:
        raise ValueError(f"mismatched salient version: {sandbox_versions[0]} vs {YMIR_REPO_VERSION}.")


def main() -> None:
    logger.info("[start up] Check existing mir repo version")
    try:
        check_mir_repo_version()
    except ValueError:
        logger.error(
            generate_msg_box(
                "Please upgrade existing mir repo with:\nbash ymir.sh upgrade",
                title="ERROR: Incompatible Mir Version",
            )
        )
        exit(errno.EPERM)
    else:
        logger.info("[start up] mir version check passed.")


if __name__ == "__main__":
    main()

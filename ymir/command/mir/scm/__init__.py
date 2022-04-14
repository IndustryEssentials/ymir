import os

from mir.scm.cmd import CmdScm
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


def Scm(root_dir: str, scm_executable: str = None) -> CmdScm:
    """Returns SCM instance that corresponds to a repo at the specified
        path.
        Args:
            root_dir (str): path to a root directory of the repo.
            scm_excutable(str): "git".
        Returns:
            mir.scm.cmd.BaseScm: SCM instance.
        """

    if scm_executable not in ["git"]:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"args error: expected git, not {scm_executable}")
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    if not os.path.isdir(root_dir):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"can not create dir: {root_dir}")
    return CmdScm(root_dir, scm_executable)

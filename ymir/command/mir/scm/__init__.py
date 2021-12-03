import os

from mir.scm.cmd import CmdScm


def Scm(root_dir: str, scm_executable: str = None) -> CmdScm:
    """Returns SCM instance that corresponds to a repo at the specified
        path.
        Args:
            root_dir (str): path to a root directory of the repo.
            scm_excutable(str): one of "dvc" or "git".
        Returns:
            mir.scm.cmd.BaseScm: SCM instance.
        """

    if scm_executable not in ["dvc", "git"]:
        raise ValueError("Args error: expect dvc or git, not %s" % scm_executable)
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    if not os.path.isdir(root_dir):
        raise ValueError("Cannot create dir: %s" % root_dir)
    return CmdScm(root_dir, scm_executable)

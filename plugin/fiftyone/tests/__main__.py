import os
import sys
import subprocess


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # --cov-report term-missing
    cmd = (
        "PYTHONPATH=$PYTHONPATH:{repo_root} pytest -vv -xs --durations=0 "
        "--cov=..".format(repo_root=repo_root)
    )
    subprocess.check_call(cmd, shell=True)


if __name__ == "__main__":
    sys.exit(main())

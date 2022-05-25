import os
import sys
import subprocess


def main(args):
    params = " ".join(sys.argv[1:])

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # --cov-report term-missing
    cmd = (
        "PYTHONPATH=$PYTHONPATH:{repo_root} pytest -vv -xs --durations=0 -n=4 "
        "--cov=fiftyone".format(repo_root=repo_root)
    )
    subprocess.check_call(cmd, shell=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

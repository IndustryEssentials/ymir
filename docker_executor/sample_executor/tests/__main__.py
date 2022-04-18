import sys
import os
import subprocess
from typing import List


def main(args: List[str]) -> int:
    module_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

    # note that env.DEFAULT_ENV_FILE_PATH will change when test
    # so there should be only ONE process / thread when test
    cmd = [f"PYTHONPATH=$PYTHONPATH:{module_root}", 'pytest', '-vv', '-x', '--durations=0']
    cmd.extend(args)

    subprocess.check_call(' '.join(cmd), shell=True)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

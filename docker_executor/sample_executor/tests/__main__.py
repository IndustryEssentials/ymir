import sys
import os
import subprocess
from typing import List


def main(args: List[str]) -> int:
    ef_module_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

    cmd = [f"PYTHONPATH=$PYTHONPATH:{ef_module_root}", 'pytest', '-vv', '-x', '--durations=0']
    cmd.extend(args)

    subprocess.check_call(' '.join(cmd), shell=True)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

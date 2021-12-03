import logging
import os
import pytest
import sys


@pytest.fixture(autouse=True)
def mir_test_executable():
    mir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    executable = os.path.join(mir_root, "mir/__main__.py")
    return "python {} -d".format(executable)


def _add_logging():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s] %(filename)s:%(lineno)s:%(funcName)s(): %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.DEBUG)


_add_logging()

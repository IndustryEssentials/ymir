import argparse
import logging
import os
import re
import sys
from concurrent import futures
from typing import Any

import grpc
import yaml

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controller import server_impl as mir_controller_service
from controller import task_monitor
from proto import backend_pb2_grpc

path_matcher = re.compile(r"\$\{([^}^{]+)\}")


def _parse_args() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='config_file', type=str, required=True, help='path to config file.')
    parser.add_argument('-d', dest='debug', action='store_true', default=False)
    return parser.parse_args()


def path_constructor(loader: Any, node: Any) -> str:
    """ Extract the matched value, expand env variable, and replace the match """
    value = node.value
    match = path_matcher.match(value)
    if not match:
        return ''
    env_var = match.group()[2:-1]
    return os.environ.get(env_var) + value[match.end():]


def parse_config_file(config_file: str) -> Any:
    yaml.add_implicit_resolver("./test.yml", path_matcher, None, yaml.SafeLoader)
    yaml.add_constructor("./test.yml", path_constructor, yaml.SafeLoader)

    with open(config_file) as f:
        return yaml.safe_load(f)


def main(main_args: Any) -> int:
    if main_args.debug:
        logging.basicConfig(stream=sys.stdout,
                            format='%(levelname)-8s: [%(asctime)s] %(filename)s:%(lineno)s:%(funcName)s(): %(message)s',
                            datefmt='%Y%m%d-%H:%M:%S',
                            level=logging.DEBUG)
        logging.debug("in debug mode")
    else:
        logging.basicConfig(stream=sys.stdout, format='%(message)s', level=logging.INFO)

    server_config = parse_config_file(main_args.config_file)
    sandbox_root = server_config['SANDBOX']['sandboxroot']
    os.makedirs(sandbox_root, exist_ok=True)

    # start task monitor
    monitor_storage_root = server_config['TASK_MONITOR']['storageroot']
    os.makedirs(monitor_storage_root, exist_ok=True)
    ctr_task_monitor = task_monitor.ControllerTaskMonitor(storage_root=monitor_storage_root)

    # start grpc server
    port = server_config['SERVICE']['port']
    mc_service_impl = mir_controller_service.MirControllerService(sandbox_root=sandbox_root,
                                                                  assets_config=server_config['ASSETS'])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    backend_pb2_grpc.add_mir_controller_serviceServicer_to_server(mc_service_impl, server)
    server.add_insecure_port("[::]:{}".format(port))
    server.start()

    logging.info("mir controller started, sandbox root: %s, port: %s", mc_service_impl.sandbox_root, port)

    server.wait_for_termination()  # message cycle started

    ctr_task_monitor.stop_monitor()

    return 0


if __name__ == "__main__":
    # usage: python controller/server.py -f <config_file_path>
    args = _parse_args()
    sys.exit(main(args))

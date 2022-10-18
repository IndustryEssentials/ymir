import argparse
import logging
import os
import re
import sys
from concurrent import futures
from distutils.util import strtobool
from typing import Any, Dict

import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2_grpc
from requests.exceptions import ConnectionError, HTTPError, Timeout
import yaml

from common_utils.sandbox_util import check_sandbox
from controller.utils import errors, metrics, utils, invoker_mapping
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2, backend_pb2_grpc


class MirControllerService(backend_pb2_grpc.mir_controller_serviceServicer):
    __slots__ = ("_sandbox_root", "_user_to_container_ids", "_docker_image_name")

    user_to_container_ids = {}  # type: Dict[str, str]

    def __init__(self, sandbox_root: str, assets_config: dict) -> None:
        self._sandbox_root = sandbox_root
        self._assets_config = assets_config

    @property
    def sandbox_root(self) -> str:
        return self._sandbox_root

    @property
    def assets_config(self) -> Dict:
        return self._assets_config

    def data_manage_request(self, request: backend_pb2.GeneralReq, context: Any) -> backend_pb2.GeneralResp:
        if request.req_type not in invoker_mapping.RequestTypeToInvoker:
            message = "unknown invoker for req_type: {}".format(request.req_type)  # type: str
            logging.error(message)
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, message)

        task_id = request.task_id
        invoker_class = invoker_mapping.RequestTypeToInvoker[request.req_type]
        invoker = invoker_class(sandbox_root=self.sandbox_root,
                                request=request,
                                assets_config=self.assets_config,
                                async_mode=True)
        try:
            invoker_result = invoker.server_invoke()
        except errors.MirCtrError as e:
            logging.exception(f"task {task_id} MirCtrError error: {e}")
            return utils.make_general_response(e.error_code, e.error_message)
        except (ConnectionError, HTTPError, Timeout) as e:
            logging.exception(f"task {task_id} HTTPError error: {e}")
            return utils.make_general_response(CTLResponseCode.INVOKER_HTTP_ERROR, str(e))
        except Exception as e:
            logging.exception(f"task {task_id} general error: {e}")
            return utils.make_general_response(CTLResponseCode.INVOKER_UNKNOWN_ERROR, str(e))

        if isinstance(invoker_result, backend_pb2.GeneralResp):
            return invoker_result

        return utils.make_general_response(CTLResponseCode.UNKOWN_RESPONSE_FORMAT,
                                           "unknown result type: {}".format(type(invoker_result)))


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
    env_value = os.environ.get(env_var)
    if not env_value:
        logging.info(f"env empty for key: {env_var}")
    return env_value + value[match.end():]


def parse_config_file(config_file: str) -> Any:
    yaml.add_implicit_resolver("!path", path_matcher, None, yaml.SafeLoader)
    yaml.add_constructor("!path", path_constructor, yaml.SafeLoader)

    with open(config_file) as f:
        return yaml.safe_load(f)


def _init_metrics(metrics_config: Dict) -> None:
    try:
        metrics_permission_pass = bool(strtobool(metrics_config['allow_feedback']))
    except (ValueError, AttributeError):  # NoneType
        metrics_permission_pass = False
    metrics_uuid = metrics_config['anonymous_uuid'] or 'anonymous_uuid'
    manager = metrics.MetricsManager(permission_pass=metrics_permission_pass,
                                     uuid=metrics_uuid,
                                     server_host=metrics_config['server_host'],
                                     server_port=metrics_config['server_port'])
    manager.send_counter('init.start')


def main(main_args: Any) -> int:
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-4s: [%(asctime)s] %(filename)s:%(lineno)-03s:\t%(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.INFO)

    server_config = parse_config_file(main_args.config_file)
    sandbox_root = server_config['SANDBOX']['sandboxroot']
    os.makedirs(sandbox_root, exist_ok=True)

    check_sandbox(sandbox_root)
    _init_metrics(server_config['METRICS'])

    # start grpc server
    port = server_config['SERVICE']['port']
    mc_service_impl = MirControllerService(sandbox_root=sandbox_root, assets_config=server_config['ASSETS'])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    backend_pb2_grpc.add_mir_controller_serviceServicer_to_server(mc_service_impl, server)

    health_pb2_grpc.add_HealthServicer_to_server(health.HealthServicer(), server)

    server.add_insecure_port("[::]:{}".format(port))
    server.start()

    logging.info("mir controller started, sandbox root: %s, port: %s", mc_service_impl.sandbox_root, port)

    server.wait_for_termination()  # message cycle started

    return 0


if __name__ == "__main__":
    # usage: python controller/server.py -f <config_file_path>
    args = _parse_args()
    sys.exit(main(args))

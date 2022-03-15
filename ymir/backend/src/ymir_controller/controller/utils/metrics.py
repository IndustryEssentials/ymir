import argparse
import logging
import sys
from typing import Any

import statsd

from controller.utils import singleton


@singleton.singleton
class MetricsManager:
    def __init__(self, permission_pass: bool, uuid: str, server_host: str, server_port: str) -> None:
        logging.info(f'Metrics init: perm-{permission_pass} uuid-{uuid} host-{server_host} port-{server_port}')
        self._permission_pass = permission_pass
        if not self._permission_pass:
            return
        if not uuid or not server_host or not server_port:
            raise RuntimeError("MetricsManager not initialized.")
        # _permission_pass indicates whether the permession is granted to record task metrics.
        self._uuid = uuid
        self._server_host = server_host
        self._server_port = int(server_port)
        self._client = statsd.StatsClient(host=self._server_host,
                                          port=self._server_port,
                                          prefix=f"ymir_metrics.{self._uuid}")

    def send_counter(self, content: str) -> None:
        if not self._permission_pass:
            return
        if not self._uuid or not self._server_host or not self._server_port:
            raise RuntimeError("MetricsManager args not initialized.")
        if not self._client:
            raise RuntimeError("MetricsManager client not initialized.")

        self._client.incr(content)
        return


def send_counter_metrics(content: str) -> None:
    # fake initializer, used to retrieval client instance.
    manager = MetricsManager(False, "uuid", "localhost", "9125")
    manager.send_counter(content)


# server as client.
def _parse_args() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, help='host name/ip to send metrics data.', default='localhost')
    parser.add_argument('--port', type=int, help='host port to send metrics data.', default=9125)
    parser.add_argument('--uuid',
                        type=str,
                        help='unique identifier, added to the head field of metrics name.',
                        default='uuid')
    parser.add_argument('--content', type=str, help='content data to be sent.', required=True)
    return parser.parse_args()


def main(main_args: Any) -> int:
    manager = MetricsManager(permission_pass=True,
                             uuid=main_args.uuid,
                             server_host=main_args.host,
                             server_port=main_args.port)
    manager.send_counter(main_args.content)
    return 0


if __name__ == "__main__":
    args = _parse_args()
    sys.exit(main(args))

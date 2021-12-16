import argparse
import logging
import socket
import sys

from typing import Any

from controller.utils import singleton


@singleton.singleton
class MetricsManager:
    def __init__(self, permission_pass: bool, uuid: str, server_host: str, server_port: str) -> None:
        if not uuid or not server_host or not server_port:
            raise RuntimeError("MetricsManager not initialized.")
        # _permission_pass indicates whether the permession is granted to record task metrics.
        self._permission_pass = permission_pass
        self._uuid = uuid
        self._server_host = server_host
        self._server_port = int(server_port)
        logging.info(f'Metrics init: perm-{permission_pass} uuid-{uuid} host-{server_host} port-{server_port}')

    def send_counter(self, content: str) -> None:
        if not self._permission_pass:
            return
        if not self._uuid or not self._server_host or not self._server_port:
            raise RuntimeError("MetricsManager not initialized.")

        self.send_udp_package(f'{self._uuid}.{content}:1|c', self._server_host, self._server_port)
        return

    @classmethod
    def send_udp_package(cls, metrics_name: str, server_host: str, server_port: int) -> None:
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.sendto(metrics_name.encode(), (server_host, server_port))


def send_counter_metrics(content: str) -> None:
    manager = MetricsManager(False, "uuid", "localhost", "9125")
    manager.send_counter(content)


# server as client.
def _parse_args() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, help='host name/ip to send metrics data.', default='localhost')
    parser.add_argument('--port', type=int, help='host port to send metrics data.', default=9125)
    parser.add_argument('--uuid', type=str, help='unique identifier, added to the head field of metrics name.', default='uuid')
    parser.add_argument('--content', type=str, help='content data to be sent.', default='test')
    return parser.parse_args()


def main(main_args: Any) -> int:
    manager = MetricsManager(permission_pass=True, uuid=main_args.uuid, server_host=main_args.host,
                             server_port=main_args.port)
    manager.send_counter(main_args.content)
    return 0


if __name__ == "__main__":
    args = _parse_args()
    sys.exit(main(args))

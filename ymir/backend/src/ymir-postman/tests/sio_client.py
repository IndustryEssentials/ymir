""" for test """

import sys
import socketio


sio = socketio.Client()


def update_taskstate(data):
    print(f"update_taskstate: {data}")


def main() -> int:
    url = sys.argv[1]
    namespace = sys.argv[2]

    print(f"connecting to url: {url}, namespace: {namespace}")

    sio.connect(url, namespaces=[namespace], socketio_path='/ws/socket.io')
    sio.on(update_taskstate, namespace=namespace)
    sio.wait()

    return 0


if __name__ == '__main__':
    # usage: python sio_client.py <url without http> <namespace>
    sys.exit(main())

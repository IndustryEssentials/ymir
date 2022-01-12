""" for test """

import sys
import socketio


sio = socketio.Client()


@sio.event(namespace='/000003')
def update_taskstate(data):
    print(f"update_taskstate: {data}")


# change your own url, path and namespace
namespace = sys.argv[1]
print(f"namespace: /{namespace}")
sio.connect('http://192.168.13.107:8090', namespaces=[f'/{namespace}'], socketio_path='/ws/socket.io')
sio.wait()

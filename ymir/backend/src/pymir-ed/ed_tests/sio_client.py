import socketio


sio = socketio.Client()


@sio.event(namespace='/000003')
def update_taskstate(data):
    print(f"update_taskstate: {data}")


# change your own url, path and namespace
sio.connect('http://192.168.13.107:8090', namespaces=['/000003'], socketio_path='/ws/socket.io')
sio.wait()

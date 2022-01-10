import socketio


sio = socketio.Client(logger=True, engineio_logger=True)


# @sio.event(namespace='/myspace')
# def connect():
#     print(f"I'm connected: {sio.sid}")
#     time.sleep(2)
#     sio.emit(event='client_message', data={'foo': 'bar_2'}, namespace='/myspace')
#     print('sent message')


# @sio.event(namespace='/myspace')
# def connect_error(data):
#     print(f"The connection failed: {data}")


# @sio.event(namespace='/myspace')
# def disconnect():
#     print("I'm disconnected!")


@sio.event(namespace='/000003')
def server_message(*args, **kwargs):
    print('server_message received with ', args, kwargs)


sio.connect('http://192.168.13.107:8090/sio', namespaces=['/000003'], socketio_path='/ws/socket.io')
sio.wait()

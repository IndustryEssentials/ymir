import logging
import sys
import time

import eventlet
import socketio


logging.basicConfig(stream=sys.stdout,
                    format='%(levelname)-8s: [%(asctime)s] %(message)s',
                    level=logging.DEBUG)

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'ed_tests/index.html'}
})


@sio.event
def connect(sid, environ, auth):
    logging.info(f"connect: {sid}, environ: {environ}, auth: {auth}")


@sio.event
def client_message(sid, data):
    logging.info(f"client_message from {sid}: {data}")
    time.sleep(1)
    sio.emit(event='server_message', data={'response': 'hello', 'sid': sid})
    logging.info('sent msg to client')


@sio.event
def disconnect(sid):
    logging.info('disconnect ', sid)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 8100)), app)

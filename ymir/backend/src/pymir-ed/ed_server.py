import logging
import sys

# import eventlet
# import socketio

from ed_src import event_handlers
from ed_src.event_dispatcher import EventDispatcher


logging.basicConfig(stream=sys.stdout,
                    format='%(levelname)-8s: [%(asctime)s] %(message)s',
                    level=logging.DEBUG)

# event dispatcher
ed = EventDispatcher(event_name='/events/taskstates')
ed.register_handler(event_handlers.on_task_state)
ed.start()
ed.wait()

import logging
import sys

from postman_src import event_handlers
from postman_src.event_dispatcher import EventDispatcher


def main() -> int:
    logging.basicConfig(stream=sys.stdout, format='%(levelname)-8s: [%(asctime)s] %(message)s', level=logging.INFO)

    # event dispatcher
    ed = EventDispatcher(event_name='/events/taskstates')
    ed.register_handler(event_handlers.on_task_state)
    ed.start()
    ed.wait()


if __name__ == '__main__':
    sys.exit(main())

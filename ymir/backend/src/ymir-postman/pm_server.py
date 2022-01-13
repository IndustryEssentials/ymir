import logging
import sys

from postman import event_handlers
from postman.event_dispatcher import EventDispatcher
from postman.settings import settings


def main() -> int:
    # for test: debug logs
    logging.basicConfig(stream=sys.stdout, format='%(levelname)-8s: [%(asctime)s] %(message)s', level=logging.DEBUG)

    logging.info(f"postman event dispatcher start with settings: {settings}")

    # event dispatcher
    ed = EventDispatcher(event_name='/events/taskstates')
    ed.register_handler(event_handlers.on_task_state)
    ed.start()


if __name__ == '__main__':
    sys.exit(main())

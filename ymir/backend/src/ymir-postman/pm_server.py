import logging
import sys

from postman import event_handlers
from postman.event_dispatcher import EventDispatcher
from postman.settings import settings


def main() -> int:
    is_debug_mode = '-d' in sys.argv

    # for test: debug logs
    log_level = logging.DEBUG if is_debug_mode else logging.INFO
    logging.basicConfig(stream=sys.stdout, format='%(levelname)-8s: [%(asctime)s] %(message)s', level=log_level)

    logging.info(f"postman event dispatcher start with settings: {settings}")

    # event dispatcher
    ed = EventDispatcher(event_name='/events/taskstates')
    ed.register_handler(event_handlers.on_task_state)
    ed.start()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

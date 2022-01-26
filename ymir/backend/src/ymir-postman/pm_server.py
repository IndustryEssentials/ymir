import logging
import sys

from postman import event_handlers
from postman.event_dispatcher import EventDispatcher
from postman.settings import settings


def main() -> None:
    is_debug_mode = '-d' in sys.argv

    # for test: debug logs
    log_level = logging.DEBUG if is_debug_mode else logging.INFO
    logging.basicConfig(stream=sys.stdout, format='%(levelname)-8s: [%(asctime)s] %(message)s', level=log_level)

    logging.info(f"postman event dispatcher start with:\n    debug: {is_debug_mode} \n    settings: {settings}")

    # event dispatcher
    EventDispatcher(event_name='/events/taskstates', handler=event_handlers.on_task_state).start()


if __name__ == '__main__':
    sys.exit(main())

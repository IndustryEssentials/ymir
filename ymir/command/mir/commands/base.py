from abc import ABC, abstractmethod
import logging
from typing import Any
from mir.tools.code import time_it


class BaseCommand(ABC):
    """base class for all commands in mir"""

    # lifecycle
    def __init__(self, args: Any):
        self.args = args

    @time_it
    def cmd_run(self) -> int:
        return self.run()

    @abstractmethod
    def run(self) -> int:
        logging.critical("BaseCommand run: this action should override in sub classes")
        return 0

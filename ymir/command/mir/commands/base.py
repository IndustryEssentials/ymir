from abc import ABC, abstractmethod
import logging
from typing import Any


class BaseCommand(ABC):
    """base class for all commands in mir"""

    # lifecycle
    def __init__(self, args: Any):
        self.args = args

    # public: abstract
    @abstractmethod
    def run(self) -> int:
        logging.critical("BaseCommand run: this action should override in sub classes")
        return 0

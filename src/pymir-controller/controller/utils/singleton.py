from typing import Dict, Callable


def singleton(cls: Callable) -> object:
    _instance = {}

    def inner(*args: tuple, **kwargs: Dict[str, dict]) -> object:
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return inner

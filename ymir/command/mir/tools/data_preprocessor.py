from enum import Enum
from typing import Any, Callable, Dict


class PreprocessType(str, Enum):
    PT_RESIZE = '_resize'
    PT_TO_FLOAT = '_to_float'
    PT_NOTHING = '_nothing'


def _prep_type_to_func(prep_type: PreprocessType) -> Callable:
    funcs: Dict[PreprocessType, Callable] = {
        PreprocessType.PT_RESIZE: _prep_func_resize,
        PreprocessType.PT_TO_FLOAT: _prep_func_to_float,
        PreprocessType.PT_NOTHING: _prep_func_nothing,
    }
    return funcs[prep_type]


# prep functions
def _prep_func_resize(input: Any, dst_w: int, dst_h: int) -> Any:
    raise NotImplementedError('not implemented yet')


def _prep_func_to_float(input: Any) -> Any:
    raise NotImplementedError('not implemented yet')


def _prep_func_nothing(input: Any) -> Any:
    return input


class DataPreprocessor:
    def __init__(self, p: dict) -> None:
        self._preprocess_args = p

    def __hash__(self) -> int:
        pass

    def read_and_preprocess(self, asset_id: str) -> bytes:
        pass

    def preprocess(self, asset_data: bytes) -> bytes:
        pass

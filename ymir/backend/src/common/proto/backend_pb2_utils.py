import enum
from proto import backend_pb2


class UnknownTypesStrategyStr(str, enum.Enum):
    STOP = 'stop'
    IGNORE = 'ignore'
    ADD = 'add'


def unknown_types_strategy_str_from_enum(
        unknown_types_strategy: backend_pb2.UnknownTypesStrategy) -> str:
    mapping = {
        backend_pb2.UnknownTypesStrategy.UTS_STOP: UnknownTypesStrategyStr.STOP,
        backend_pb2.UnknownTypesStrategy.UTS_IGNORE: UnknownTypesStrategyStr.IGNORE,
        backend_pb2.UnknownTypesStrategy.UTS_ADD: UnknownTypesStrategyStr.ADD,
    }
    return mapping[unknown_types_strategy].value

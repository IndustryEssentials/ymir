import enum
from proto import backend_pb2


class UnknownTypesStrategyStr(str, enum.Enum):
    STOP = 'stop'
    IGNORE = 'ignore'
    ADD = 'add'


def unknown_types_strategy_str_from_enum(
        unknown_types_strategy: backend_pb2.UnknownTypesStrategy) -> UnknownTypesStrategyStr:
    mapping = {
        backend_pb2.UnknownTypesStrategy.UTS_STOP: UnknownTypesStrategyStr.STOP,
        backend_pb2.UnknownTypesStrategy.UTS_IGNORE: UnknownTypesStrategyStr.IGNORE,
        backend_pb2.UnknownTypesStrategy.UTS_ADD: UnknownTypesStrategyStr.ADD,
    }
    return mapping[unknown_types_strategy]


def unknown_types_strategy_enum_from_str(
        unknown_types_strategy: UnknownTypesStrategyStr) -> backend_pb2.UnknownTypesStrategy:
    mapping = {
        UnknownTypesStrategyStr.STOP: backend_pb2.UnknownTypesStrategy.UTS_STOP,
        UnknownTypesStrategyStr.IGNORE: backend_pb2.UnknownTypesStrategy.UTS_IGNORE,
        UnknownTypesStrategyStr.ADD: backend_pb2.UnknownTypesStrategy.UTS_ADD,
    }
    return mapping[unknown_types_strategy]

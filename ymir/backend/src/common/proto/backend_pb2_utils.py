from proto import backend_pb2


def unknown_types_strategy_str_from_enum(unknown_types_strategy: backend_pb2.UnknownTypesStrategy) -> str:
    mapping = {
        backend_pb2.UnknownTypesStrategy.UTS_STOP: 'stop',
        backend_pb2.UnknownTypesStrategy.UTS_IGNORE: 'ignore',
        backend_pb2.UnknownTypesStrategy.UTS_ADD: 'add'
    }
    return mapping[unknown_types_strategy]


def unknown_types_strategy_enum_from_str(unknown_types_strategy: str) -> backend_pb2.UnknownTypesStrategy:
    mapping = {
        'stop': backend_pb2.UnknownTypesStrategy.UTS_STOP,
        'ignore': backend_pb2.UnknownTypesStrategy.UTS_IGNORE,
        'add': backend_pb2.UnknownTypesStrategy.UTS_ADD
    }
    return mapping[unknown_types_strategy]

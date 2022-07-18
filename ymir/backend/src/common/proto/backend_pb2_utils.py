from proto import backend_pb2


def strategy_str_from_enum(unknown_types_strategy: backend_pb2.UnknownTypesStrategy) -> str:
    mapping = {
        backend_pb2.UnknownTypesStrategy.UTS_STOP: 'stop',
        backend_pb2.UnknownTypesStrategy.UTS_IGNORE: 'ignore',
        backend_pb2.UnknownTypesStrategy.UTS_ADD: 'add'
    }
    return mapping[unknown_types_strategy]
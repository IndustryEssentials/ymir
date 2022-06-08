from enum import unique, IntEnum


@unique
class DataSetResultTypes(IntEnum):
    GROUND_TRUTH = 0  # ground_truth
    PREDICTION = 1  # prediction

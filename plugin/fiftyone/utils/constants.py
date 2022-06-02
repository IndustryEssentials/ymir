from enum import unique, Enum


@unique
class DataSetResultTypes(str, Enum):
    GROUND_TRUTH = "ground_truth"
    PREDICTION = "prediction"

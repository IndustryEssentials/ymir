from enum import IntEnum


class TaskState(IntEnum):
    TS_RUNNING = 2
    TS_ERROR = 4


class TaskReturnCode(IntEnum):
    TRC_NOTSET = 0

    # dataset and config errors
    # can not read config file, or can not find required arguments
    TRC_CONFIG_ERROR = 180001
    # Can not find training dataset or validation dataset
    TRC_DATASET_ERROR = 180002
    # Can not read image, or image format unknown
    TRC_UNKNOWN_IMAGE_FORMAT = 180003
    # Can not find model file
    TRC_MODEL_ERROR = 180004

    # cuda, gpu and memory errors
    # CUDA and GPU mismatch
    TRC_CUDA_GPU_ERROR = 180101
    # Can not find any GPUs if GPU is needed
    TRC_NO_GPU = 180102
    # Out of memory
    TRC_OOM = 180103

    # numeral errors
    # Find NaN when training
    TRC_NAN_ERROR = 180201

    # misc
    # Network error occured when download
    TRC_NETWORK_ERROR = 180301
from enum import IntEnum


class ExecutorState(IntEnum):
    ES_RUNNING = 2
    ES_ERROR = 4


class ExecutorReturnCode(IntEnum):
    RC_EXEC_NO_ERROR = 0

    # dataset and config errors
    # can not read config file, or can not find required arguments
    RC_EXEC_CONFIG_ERROR = 180001
    # Can not find training dataset or validation dataset
    RC_EXEC_DATASET_ERROR = 180002
    # Can not read image, or image format unknown
    RC_EXEC_UNKNOWN_IMAGE_FORMAT = 180003
    # Can not find model file
    RC_EXEC_MODEL_ERROR = 180004

    # cuda, gpu and memory errors
    # CUDA and GPU mismatch
    RC_EXEC_CUDA_GPU_ERROR = 180101
    # Can not find any GPUs if GPU is needed
    RC_EXEC_NO_GPU = 180102
    # Out of memory
    RC_EXEC_OOM = 180103

    # numeral errors
    # Find NaN when training
    RC_EXEC_NAN_ERROR = 180201

    # misc
    # Network error occured when download
    RC_EXEC_NETWORK_ERROR = 180301

    # other errors
    RC_CMD_CONTAINER_ERROR = 160004

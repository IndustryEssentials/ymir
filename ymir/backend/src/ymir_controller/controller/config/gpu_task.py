import os

# key of locking gpu
GPU_LOCKING_SET = "gpu_locking_set"

# gpu usage for dispach
GPU_USAGE_THRESHOLD = float(os.environ.get("GPU_USAGE_THRESHOLD", 0.8))
# gpu lock time
GPU_LOCK_MINUTES = int(os.environ.get("GPU_LOCK_MINUTES", 3))

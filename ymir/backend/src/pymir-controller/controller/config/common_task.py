import os

# redis service
CTR_REDIS_URI = os.environ.get("CTR_REDIS_URI", "redis://:@127.0.0.1:6379")

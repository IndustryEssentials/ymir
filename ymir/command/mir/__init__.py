import logging
import sys

logging.basicConfig(stream=sys.stdout,
                    format='%(levelname)-4s: [%(asctime)s] %(filename)s:%(lineno)-03s: %(message)s',
                    datefmt='%Y%m%d-%H:%M:%S',
                    level=logging.INFO)

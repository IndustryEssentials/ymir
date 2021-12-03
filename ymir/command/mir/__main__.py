""" entry point for mir command line tools """

import sys

from mir.main import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

from typing import List
from mir.cli import create_main_parser


def main(argv: List[str] = None) -> int:
    """
    Run dvc CLI command.
    Args:
        argv: optional list of arguments to parse.
    Returns:
        int: command's return code.
    """

    # parse and exec
    argument_parser = create_main_parser()
    args = argument_parser.parse_args(argv)
    if hasattr(args, 'func'):
        cmd = args.func(args)  # see cli.py: bind_to_subparsers for all elements in _COMMANDS_
        return cmd.run()

    argument_parser.print_help()
    return -1

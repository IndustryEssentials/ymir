"""mir command line interface"""
import argparse
import logging
import os
import sys
from typing import Any, cast, Protocol

from mir import version
from mir.commands import (init, checkout, commit, copy, export, filter, fuse, merge,
                          sampling, show, status, training, mining, import_dataset, import_model, infer)

_COMMANDS_ = [
    init, checkout, commit, copy, export, filter, fuse, merge, sampling, show, status, training, mining,
    import_dataset, import_model, infer
]


class _CmdModuleProtocol(Protocol):
    """
    protocol for all modules in `_COMMANDS_`, to cheat mypy
    """
    @staticmethod
    def bind_to_subparsers(sub_parsers: argparse.Action, share_parser: argparse.ArgumentParser) -> None:
        pass


class MirParser(argparse.ArgumentParser):
    """Custom parser class for mir CLI."""
    def error(self, message: str, cmd_cls: str = None) -> Any:  # pylint: disable=arguments-differ
        logging.error(message)

    def parse_args(self, args: Any = None, namespace: Any = None) -> Any:
        # NOTE: overriding to provide a more granular help message.
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            msg = "unrecognized arguments: %s"
            self.error(msg % " ".join(argv), getattr(args, "func", None))
        # add default user labels if necessary
        if not args.label_storage_file:
            args.label_storage_file = os.path.join(args.mir_root, '.mir', 'labels.yaml')
        return args


class VersionAction(argparse.Action):
    """Show mir version and exits"""
    def __call__(self, parser: Any, namespace: Any, values: Any, option_string: Any = None) -> None:
        logging.info(f"mir version: {version.YMIR_VERSION}")
        sys.exit(0)


class DebugModeAction(argparse.Action):
    """Work in debug mode, and print debug info."""
    def __call__(self, parser: Any, namespace: Any, values: Any, option_string: Any = None) -> None:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(stream=sys.stdout,
                            format='%(levelname)-8s: [%(asctime)s] %(filename)s:%(lineno)-03s: %(message)s',
                            datefmt='%Y%m%d-%H:%M:%S',
                            level=logging.DEBUG)
        logging.debug("in debug mode")


def create_main_parser() -> argparse.ArgumentParser:
    parent_parser = argparse.ArgumentParser()
    main_parser = MirParser(
        prog="mir",
        description="MIR",
        parents=[parent_parser],
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )

    main_parser.add_argument("-v", "--version", nargs=0, action=VersionAction, help="show program's version")

    main_parser.add_argument("-d", "--debug", nargs=0, action=DebugModeAction, help="set debug mode, print more infos.")

    share_parser = argparse.ArgumentParser(add_help=False)
    share_parser.add_argument("--root",
                              "-r",
                              dest="mir_root",
                              type=str,
                              default=os.getcwd(),
                              help="Root path to the mir repo, use . if not set.")
    share_parser.add_argument("--user-label-file",
                              dest="label_storage_file",
                              type=str,
                              default='',
                              required=False,
                              help="Path to user label file, use .mir/labels.yaml if not set")

    # sub parsers
    subparsers = main_parser.add_subparsers(title="sub commands",
                                            metavar="COMMAND",
                                            dest="cmd",
                                            help="Use mir COMMAND --help for sub command help")

    for command in _COMMANDS_:
        cast(_CmdModuleProtocol, command).bind_to_subparsers(subparsers, share_parser)

    return main_parser

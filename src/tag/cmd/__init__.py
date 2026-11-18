"""Shared command entry handling and diagnostics."""

import logging
import sys
from collections.abc import Callable
from functools import wraps
from pathlib import Path

from ..library import Library

logger = logging.getLogger(__name__)


def die(message: str) -> int:
    logger.error("%s", message)
    return 1


def usage(arguments: str) -> ValueError:
    """Build a usage error using the invoked executable name."""
    return ValueError(f"Usage: {Path(sys.argv[0]).name} {arguments}".rstrip())


def _no_arguments(argv: list[str]) -> tuple[()]:
    if argv:
        raise usage("")
    return ()


def command(
    *, parse: Callable[[list[str]], tuple[object, ...]]
) -> Callable[[Callable[..., int]], Callable[[], int]]:
    """Parse positional arguments before discovering and injecting the library."""
    def decorate(handler: Callable[..., int]) -> Callable[[], int]:
        @wraps(handler)
        def main() -> int:
            logging.basicConfig(format="%(message)s", level=logging.WARNING)
            try:
                arguments = parse(sys.argv[1:])
                library = Library.discover()
                return handler(*arguments, library=library)
            except (OSError, ValueError) as error:
                return die(str(error))

        return main

    return decorate

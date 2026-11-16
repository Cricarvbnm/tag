"""Shared command entry handling."""

import sys
from collections.abc import Callable
from pathlib import Path

from .library import find_root


def die(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def entry(handler: Callable[[list[str], Path], int]) -> None:
    try:
        status = handler(sys.argv[1:], find_root())
    except (OSError, ValueError) as error:
        status = die(str(error))
    raise SystemExit(status)

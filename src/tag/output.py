"""Path display and confirmation."""

import os
import shlex
import subprocess
import sys
from pathlib import Path

from .library import relative


def confirm(prompt: str) -> bool:
    """Accept only a lowercase y; EOF cancels the action."""
    print("\n" + prompt, end="", flush=True)
    return sys.stdin.readline().rstrip("\n") == "y"


def list_paths(paths: list[Path], root: Path) -> int:
    command = shlex.split(os.environ.get("TAG_LISTER", "ls -1"))
    if not command:
        raise ValueError("TAG_LISTER must not be empty")
    return subprocess.run([*command, "-d", *(relative(path, root) for path in paths)], cwd=root).returncode


def print_tree(paths: list[Path], root: Path) -> None:
    tree: dict = {}
    for path in sorted(set(paths), key=lambda item: str(item).split("/")):
        node = tree
        for part in Path(relative(path, root)).parts:
            node = node.setdefault(part, {})

    def draw(node: dict, prefix: str = "") -> None:
        items = sorted(node.items())
        for index, (name, children) in enumerate(items):
            last = index == len(items) - 1
            print(prefix + ("└── " if last else "├── ") + name)
            if children:
                draw(children, prefix + ("    " if last else "│   "))

    draw(tree)



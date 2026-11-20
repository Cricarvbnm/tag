"""Display resource paths using the configured external lister."""

import os
import shlex
import subprocess
import sys
from pathlib import Path


def _relative(path: Path, root: Path) -> str:
    """Format a path relative to the display root when possible."""
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return str(path)


def list_paths(paths: list[Path]) -> int:
    if not paths:
        return 0
    command = shlex.split(os.environ.get("TAG_LISTER") or "ls -1")
    if not command:
        raise ValueError("TAG_LISTER must contain a command")
    return subprocess.run([*command, "-d", "--", *(_relative(path, Path.cwd()) for path in paths)]).returncode


def confirm(prompt: str) -> bool:
    """Accept only lowercase y; EOF cancels."""
    print("\n" + prompt, end="", flush=True)
    return sys.stdin.readline().rstrip("\n") == "y"


def print_tree(
    paths: list[Path], root: Path, formats: dict[Path, str] | None = None,
) -> None:
    """Draw paths with per-node format strings, defaulting to ' {name}'.

    Format keys are absolute paths. Literal braces in templates must be doubled.
    """
    tree: dict = {}
    for path in sorted(set(paths), key=lambda path: str(path).split("/")):
        node = tree
        for part in Path(_relative(path, root)).parts:
            node = node.setdefault(part, {})

    def draw(node: dict, parent: Path, prefix: str = "") -> None:
        items = sorted(node.items())
        for index, (name, children) in enumerate(items):
            last = index == len(items) - 1
            path = Path(os.path.abspath(parent / name))
            template = (formats or {}).get(path, " {name}")
            print(prefix + ("└──" if last else "├──") + template.format(name=name))
            if children:
                draw(children, path, prefix + ("    " if last else "│   "))

    draw(tree, root)

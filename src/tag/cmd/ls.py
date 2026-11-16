from pathlib import Path

from ..common import die, entry
from ..library import find_resources
from ..output import list_paths


def run(argv: list[str], library: Path) -> int:
    if len(argv) != 1:
        return die("Usage: tag-ls <tag>")
    paths = find_resources(Path(argv[0]))
    return list_paths(paths, library) if paths else 0


def main() -> None:
    entry(run)

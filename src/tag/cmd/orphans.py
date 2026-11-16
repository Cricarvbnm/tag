from pathlib import Path

from ..common import entry
from ..library import find_resources
from ..output import list_paths


def run(argv: list[str], library: Path) -> int:
    tagged = set(find_resources(library / "tag"))
    resources = {path.absolute() for path in (library / "res").iterdir()}
    return list_paths(sorted(resources - tagged), library)


def main() -> None:
    entry(run)

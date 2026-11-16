import os
from pathlib import Path

from ..common import die, entry


def run(argv: list[str], library: Path) -> int:
    if len(argv) < 2:
        return die("Usage: tag-add <resource> <tag>...")
    resource = Path(argv[0])
    for name in argv[1:]:
        tag = Path(name)
        tag.mkdir(parents=True, exist_ok=True)
        os.symlink(os.path.relpath(resource.absolute(), tag.absolute()), tag / resource.name)
    return 0


def main() -> None:
    entry(run)

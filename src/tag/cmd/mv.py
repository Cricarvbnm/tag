import os
import shutil
from pathlib import Path

from ..common import die, entry
from ..library import find_resource_links


def run(argv: list[str], library: Path) -> int:
    if len(argv) != 2:
        return die("Usage: tag-mv <old> <new>")
    old, new = map(Path, argv)
    links = find_resource_links(old, library)
    shutil.move(old, new)
    for link in links:
        link.unlink()
        os.symlink(os.path.relpath(new.absolute(), link.parent.absolute()), link)
    return 0


def main() -> None:
    entry(run)

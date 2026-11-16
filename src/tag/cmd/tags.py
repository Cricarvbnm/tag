from pathlib import Path

from ..common import die, entry
from ..library import find_resource_links
from ..output import print_tree


def run(argv: list[str], library: Path) -> int:
    if len(argv) != 1:
        return die("Usage: tag-tags <resource>")
    links = find_resource_links(Path(argv[0]), library)
    if links:
        print_tree([path.parent for path in links], library)
    return 0


def main() -> None:
    entry(run)

from pathlib import Path

from ..common import die, entry
from ..library import find_resource_links
from ..output import confirm, print_tree


def run(argv: list[str], library: Path) -> int:
    if not argv:
        return die("Usage: tag-rm <resource> [<tag>...]")
    resource = Path(argv[0])
    if len(argv) > 1:
        for name in argv[1:]:
            link = Path(name) / resource.name
            link.unlink(missing_ok=True)
            print(f"removed '{link}'")
        return 0
    links = find_resource_links(resource, library)
    if links:
        print_tree([path.parent for path in links], library)
        if confirm("Remove these tags? [y/N] "):
            for link in links:
                link.unlink(missing_ok=True)
    return 0


def main() -> None:
    entry(run)

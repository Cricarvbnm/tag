"""Remove resource links from selected tags or after confirmation."""

from pathlib import Path

from ..library import Library, Resource, Tag
from ..output import confirm, print_tree
from . import command, usage


def _parse(argv: list[str]) -> tuple[Path, tuple[Path, ...]]:
    if not argv:
        raise usage("<resource> [<tag>...]")
    return Path(argv[0]), tuple(Path(name) for name in argv[1:])


@command(parse=_parse)
def main(resource: Path, tags: tuple[Path, ...], *, library: Library) -> int:
    target = Resource(resource)
    if tags:
        for path in tags:
            for removed in Tag(path).remove(target):
                print(f"removed '{removed.path}'")
    else:
        links = library.links(target)
        if links:
            print_tree([link.path.parent for link in links], library.root)
            if confirm("Remove these tags? [y/N] "):
                for link in links:
                    link.remove()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

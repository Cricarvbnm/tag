"""Show the tag directories referring to a resource."""

from pathlib import Path

from ..library import Library, Resource
from ..output import print_tree
from . import command, usage


def _parse(argv: list[str]) -> tuple[Path]:
    if len(argv) != 1:
        raise usage("<resource>")
    return (Path(argv[0]),)


@command(parse=_parse)
def main(path: Path, *, library: Library) -> int:
    links = library.links(Resource(path))
    print_tree([link.path.parent for link in links], library.root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

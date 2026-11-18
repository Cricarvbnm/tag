"""List resources in a tag and its descendants."""

from pathlib import Path

from ..library import Library, Tag
from ..output import list_paths
from . import command, usage


def _parse(argv: list[str]) -> tuple[Path]:
    if len(argv) != 1:
        raise usage("<tag>")
    return (Path(argv[0]),)


@command(parse=_parse)
def main(path: Path, *, library: Library) -> int:
    resources = Tag.from_path(path).resources()
    return list_paths(sorted((resource.path for resource in resources), key=str), library.root)


if __name__ == "__main__":
    raise SystemExit(main())

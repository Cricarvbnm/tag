"""Link a resource into one or more tags."""

from pathlib import Path

from ..library import Library, Resource, Tag
from . import command, usage


def _parse(argv: list[str]) -> tuple[Path, tuple[Path, ...]]:
    if len(argv) < 2:
        raise usage("<resource> <tag>...")
    return Path(argv[0]), tuple(Path(name) for name in argv[1:])


@command(parse=_parse)
def main(resource: Path, tags: tuple[Path, ...], *, library: Library) -> int:
    existing = Resource.from_path(resource)
    for path in tags:
        Tag(path).add(existing)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

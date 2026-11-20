"""Link a resource into one or more tags."""

import os
from pathlib import Path

from ..library import Library, Resource, Tag
from ..output import print_tree
from . import command, usage


def _parse(argv: list[str]) -> tuple[Path, tuple[Path, ...]]:
    if len(argv) < 2:
        raise usage("<resource> <tag>...")
    return Path(argv[0]), tuple(Path(name) for name in argv[1:])


@command(parse=_parse)
def main(resource: Path, tags: tuple[Path, ...], *, library: Library) -> int:
    existing = Resource.from_path(resource)
    formats: dict[Path, str] = {}
    for path in tags:
        directory = Path(os.path.abspath(path))
        for parent in (directory, *directory.parents):
            if parent == Path(os.path.abspath(library.root)) or parent == parent.parent:
                break
            formats.setdefault(parent, " {name}" if parent.is_dir() else "+ {name}")
        Tag(path).add(existing)
        link = directory / existing.path.name
        target = str(link.readlink()).replace("{", "{{").replace("}", "}}")
        formats[link] = " {name} -> " + target
    print_tree(list(formats), library.root, formats)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

"""Move a resource and update its referring links."""

from pathlib import Path

from ..library import Library, Resource
from . import command, usage


def _parse(argv: list[str]) -> tuple[Path, Path]:
    if len(argv) != 2:
        raise usage("<old> <new>")
    return Path(argv[0]), Path(argv[1])


@command(parse=_parse)
def main(source: Path, destination: Path, *, library: Library) -> int:
    library.move(Resource(source), destination)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

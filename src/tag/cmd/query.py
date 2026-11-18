"""Parse tag expressions and display their matching resources."""

from pathlib import Path

from ..library import Library, Tag
from ..output import list_paths
from ..query import Query
from . import command


def _parse(argv: list[str]) -> tuple[Query]:
    all_of: list[Tag] = []
    any_of: list[Tag] = []
    none_of: list[Tag] = []
    group = all_of
    for argument in argv:
        match argument:
            case "+":
                group = any_of
            case "-":
                group = none_of
            case _:
                group.append(Tag(Path(argument)))
    return (Query(tuple(all_of), tuple(any_of), tuple(none_of)),)


@command(parse=_parse)
def main(query: Query, *, library: Library) -> int:
    resources = query.evaluate(library)
    return list_paths(sorted((resource.path for resource in resources), key=str), library.root)


if __name__ == "__main__":
    raise SystemExit(main())

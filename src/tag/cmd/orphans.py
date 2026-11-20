"""List immediate resource children without tag links."""

from ..library import Library
from ..output import list_paths
from . import _no_arguments, command


@command(parse=_no_arguments)
def main(*, library: Library) -> int:
    return list_paths([resource.path for resource in library.orphans()])


if __name__ == "__main__":
    raise SystemExit(main())

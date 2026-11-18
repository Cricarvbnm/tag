"""Interactively remove broken links and stray files from the tag tree."""

from ..library import Library
from ..output import confirm, list_paths
from . import _no_arguments, command


@command(parse=_no_arguments)
def main(*, library: Library) -> int:
    broken = library.broken_links()
    if broken:
        status = list_paths([link.path for link in broken], library.root)
        if status:
            return status
        if confirm("Remove broken links? [y/N] "):
            for link in broken:
                link.remove()

    stray = library.stray_files()
    if stray:
        status = list_paths(stray, library.root)
        if status:
            return status
        if confirm("Remove stray files? [y/N] "):
            for path in stray:
                path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

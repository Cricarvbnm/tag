"""Library discovery and file scans."""

import os
from pathlib import Path


def find_root() -> Path:
    configured = os.environ.get("TAG_ROOT")
    if configured is not None:
        candidate = Path(configured).expanduser()
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        if (candidate / "res").is_dir() and (candidate / "tag").is_dir():
            return candidate
        raise FileNotFoundError(f"Invalid TAG_ROOT '{configured}': expected res/ and tag/")
    for candidate in (Path.cwd(), *Path.cwd().parents):
        if (candidate / "res").is_dir() and (candidate / "tag").is_dir():
            return candidate
    raise FileNotFoundError("Library not found: expected res/ and tag/")


def relative(path: Path, root: Path) -> str:
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return str(path)


def read_link_target(link: Path) -> Path | None:
    """Normalize a link target without following further symlinks."""
    try:
        target = Path(os.readlink(link))
        return Path(os.path.abspath(target if target.is_absolute() else link.parent / target))
    except OSError:
        return None


def find_resources(tag: Path) -> list[Path]:
    if not tag.is_dir():
        raise FileNotFoundError(f"Tag not found: '{tag}'")
    paths = set()
    for link in tag.rglob("*"):
        if link.is_symlink() and (target := read_link_target(link)) is not None:
            paths.add(target)
    return sorted(paths, key=str)


def find_resource_links(resource: Path, library: Path) -> list[Path]:
    if not resource.exists() and not resource.is_symlink():
        raise FileNotFoundError(f"Resource not found: {resource}")
    expected = Path(os.path.abspath(resource))
    library = library.absolute()
    links = [p for p in (library / "tag").rglob("*") if p.is_symlink() and read_link_target(p) == expected]
    return sorted(set(links), key=str)



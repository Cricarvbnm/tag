"""Library discovery and file scans."""

import os
import stat
import shutil
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Tag:
    """A tag directory, interpreted relative to the working directory.

    Direct construction stores the path without validation.
    """

    path: Path

    @classmethod
    def from_path(cls, path: Path) -> Tag:
        """Return an existing tag directory."""
        if not stat.S_ISDIR(path.stat().st_mode):
            raise NotADirectoryError(f"Not a tag directory: '{path}'")
        return cls(path)

    def add(self, resource: Resource) -> None:
        """Ensure the directory exists and link the supplied resource path."""
        self.path.mkdir(parents=True, exist_ok=True)
        Link(self.path / resource.path.name).create(resource)

    def remove(self, resource: Resource) -> list[Link]:
        """Remove links to the resource throughout this tag's descendants."""
        expected = Path(os.path.abspath(resource.path))
        links = [link for link in self.links() if link.target == expected]
        for link in links:
            link.remove()
        return links

    def walk(self) -> Iterator[Path]:
        """Recursively yield entries without descending through symlinks."""
        yield from self.path.rglob("*")

    def resources(self) -> set[Resource]:
        """Collect unique resources recursively across this tag's descendants."""
        return {Resource.from_link(link.path) for link in self.links()}

    def links(self) -> list[Link]:
        return [Link(path) for path in sorted(self.walk(), key=str) if path.is_symlink()]

    def broken_links(self) -> list[Link]:
        broken = []
        for link in self.links():
            try:
                link.path.stat()
            except (FileNotFoundError, NotADirectoryError):
                broken.append(link)
        return broken

    def stray_files(self) -> list[Path]:
        return sorted(
            (path for path in self.walk() if not path.is_symlink() and not path.is_dir()),
            key=str,
        )


@dataclass(frozen=True)
class Resource:
    """A resource path that can be linked into tag directories.

    Direct construction stores the path without validation.
    """

    path: Path

    @classmethod
    def from_path(cls, path: Path) -> Resource:
        """Return an existing resource."""
        path.stat()
        return cls(path)

    @classmethod
    def from_link(cls, link: Path) -> Resource:
        """Read a link target without following any further symlinks."""
        return cls.from_path(Link(link).target)

@dataclass(frozen=True)
class Link:
    """A tag entry whose target may be missing.

    Direct construction stores the path without validation.
    """

    path: Path

    @property
    def target(self) -> Path:
        """Read the target without following additional symlinks."""
        target = Path(os.readlink(self.path))
        return Path(os.path.abspath(target if target.is_absolute() else self.path.parent / target))

    def create(self, resource: Resource) -> None:
        target = os.path.relpath(resource.path.absolute(), self.path.parent.absolute())
        self.path.symlink_to(target)

    def remove(self) -> None:
        self.path.unlink(missing_ok=True)


@dataclass(frozen=True)
class Library:
    """A library root containing resources and a recursive tag tree.

    Direct construction stores the path without validation.
    """

    root: Path

    @property
    def resource_directory(self) -> Path:
        return self.root / "res"

    @property
    def tags(self) -> Tag:
        return Tag(self.root / "tag")

    def links(self, resource: Resource | None = None) -> list[Link]:
        """List tag links, optionally selecting references to a resource."""
        if resource is None:
            return self.tags.links()
        else:
            resource.path.lstat()
            expected = Path(os.path.abspath(resource.path))
            return [link for link in self.tags.links() if link.target == expected]

    def orphans(self) -> list[Resource]:
        tagged = {link.target for link in self.links()}
        resources = {Path(os.path.abspath(path)) for path in self.resource_directory.iterdir()}
        return [Resource(path) for path in sorted(resources - tagged, key=str)]

    def broken_links(self) -> list[Link]:
        return self.tags.broken_links()

    def stray_files(self) -> list[Path]:
        return self.tags.stray_files()

    def move(self, resource: Resource, destination: Path) -> Resource:
        """Move a resource and repoint its existing tag entries."""
        links = self.links(resource)
        name = resource.path.name if destination.is_dir() else destination.name
        for link in links:
            target = link.path.with_name(name)
            if target == link.path:
                continue
            try:
                target.lstat()
            except FileNotFoundError:
                pass
            else:
                raise FileExistsError(f"Tag entry already exists: '{target}'")
        moved = Resource(Path(shutil.move(str(resource.path), str(destination))))
        for link in links:
            link.remove()
            Link(link.path.with_name(moved.path.name)).create(moved)
        return moved

    @classmethod
    def from_path(cls, root: Path) -> Library:
        """Return a valid library."""
        if not cls.is_valid(root):
            raise FileNotFoundError(f"Invalid library '{root}': expected res/ and tag/")
        return cls(root)

    @staticmethod
    def is_valid(root: Path) -> bool:
        return (root / "res").is_dir() and (root / "tag").is_dir()

    @classmethod
    def discover(cls) -> Library:
        configured = os.environ.get("TAG_ROOT")
        if configured:
            candidate = Path(configured).expanduser()
            if not candidate.is_absolute():
                candidate = Path.cwd() / candidate
            return cls.from_path(candidate)
        else:
            for candidate in (Path.cwd(), *Path.cwd().parents):
                if cls.is_valid(candidate):
                    return cls(candidate)
            raise FileNotFoundError("Library not found: expected res/ and tag/")

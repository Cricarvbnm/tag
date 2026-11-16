from pathlib import Path

from ..common import entry
from ..output import confirm, list_paths


def run(argv: list[str], library: Path) -> int:
    tagroot = library / "tag"
    groups = (
        ([p for p in tagroot.rglob("*") if p.is_symlink() and not p.exists()], "Remove broken links? [y/N] "),
        ([p for p in tagroot.rglob("*") if not p.is_symlink() and not p.is_dir()], "Remove stray files? [y/N] "),
    )
    for entries, prompt in groups:
        if entries:
            list_paths(entries, library)
            if confirm(prompt):
                for entry in entries:
                    entry.unlink(missing_ok=True)
    return 0


def main() -> None:
    entry(run)

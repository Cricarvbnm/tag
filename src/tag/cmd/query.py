from pathlib import Path

from ..common import die, entry
from ..library import find_resources
from ..output import list_paths


def run(argv: list[str], library: Path) -> int:
    and_tags: list[Path] = []
    or_tags: list[Path] = []
    not_tags: list[Path] = []
    mode = "and"
    for arg in argv:
        if arg == "+":
            mode = "or"
        elif arg == "-":
            mode = "not"
        else:
            {"and": and_tags, "or": or_tags, "not": not_tags}[mode].append(Path(arg))
    if not (and_tags or or_tags or not_tags):
        return list_paths(find_resources(library / "tag"), library)
    for tag in and_tags + or_tags + not_tags:
        if not tag.is_dir():
            return die(f"Tag not found: '{tag}'")
    if or_tags:
        candidates = set().union(*(find_resources(tag) for tag in or_tags))
    else:
        candidates = set(find_resources(library / "tag"))
    for tag in and_tags:
        candidates.intersection_update(find_resources(tag))
    for tag in not_tags:
        candidates.difference_update(find_resources(tag))
    return list_paths(sorted(candidates), library)


def main() -> None:
    entry(run)

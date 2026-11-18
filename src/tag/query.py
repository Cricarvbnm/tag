"""Tag query expressions, independent of command dispatch and display."""

from dataclasses import dataclass

from .library import Library, Resource, Tag


@dataclass(frozen=True)
class Query:
    """Select resources matching every all_of, any any_of, and no none_of tags."""

    all_of: tuple[Tag, ...] = ()
    any_of: tuple[Tag, ...] = ()
    none_of: tuple[Tag, ...] = ()

    def evaluate(self, library: Library) -> set[Resource]:
        """Evaluate named tags, using the library only without positive tags.

        Each distinct named tag is validated and scanned once per evaluation.
        """
        resources = {
            tag: Tag.from_path(tag.path).resources()
            for tag in dict.fromkeys((*self.all_of, *self.any_of, *self.none_of))
        }

        if self.any_of:
            candidates: set[Resource] = set()
            for tag in self.any_of:
                candidates |= resources[tag]
        elif self.all_of:
            candidates = resources[self.all_of[0]].copy()
        else:
            root = library.tags
            candidates = resources[root].copy() if root in resources else root.resources()

        for tag in self.all_of:
            candidates &= resources[tag]
        for tag in self.none_of:
            candidates -= resources[tag]
        return candidates

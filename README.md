# tag

A Python command-line tool for tagging files and directories. Real resources stay
in `res/`; each tag is a directory of relative symlinks pointing at them. Tags
can be nested, and a resource can belong to several tags.

## Setup

The project uses `uv` and requires the Python version declared in `.python-version`.
There are no runtime Python dependencies.

```sh
uv sync
uv tool install .
```

The installation provides `tag-add`, `tag-query`, `tag-ls`, `tag-tags`,
`tag-orphans`, `tag-mv`, `tag-rm`, and `tag-fix`.
`make install PREFIX="$HOME/.local"` installs them under the selected prefix.
`make` (or `make all`) builds a source distribution and wheel in `dist/`;
`make clean` removes those package archives. `make install` builds first, then
installs the wheel into an isolated uv tool environment. `PREFIX` defaults to
`/usr/local`; `BINDIR` and `TOOL_DIR` default to `$(PREFIX)/bin` and
`$(PREFIX)/lib/uv/tools`. `UV`, `PYTHON`, and `DISTDIR` can also be overridden.
Installation prefixes are final locations; staged `DESTDIR` installation is
not supported because uv tool environments contain absolute paths.

The current version is `0.1.0`. Versions are incremented for releases rather
than for every commit; tracking the main branch is an installation choice.

Commands can also be run as Python modules:

```sh
python -m tag.cmd.add <resource> <tag>...
python -m tag.cmd.query [tags...]
```

## Library root and configuration

A library contains fixed `res/` and `tag/` directories. If `TAG_ROOT` is nonempty,
that directory must contain both directories or the command reports an error.
Otherwise, commands search upward from the current directory and use the first
matching ancestor. If none exists, the same root error is reported.

`TAG_LISTER` configures the external command used for ordinary file lists. It
defaults to `ls -1`; shell-style quoting is supported. The command must accept
`-d --` followed by paths, where `--` ends option parsing. Empty results do not
invoke the command.

Empty environment variable values are treated as unset: an empty `TAG_ROOT`
uses upward library discovery, and an empty `TAG_LISTER` uses `ls -1`.

## Commands

| Command | Arguments | Purpose |
| --- | --- | --- |
| `tag-add` | `<resource> <tag>...` | Link an existing resource into tags |
| `tag-query` | `[tags...]` | Filter resources by tag expressions |
| `tag-ls` | `<tag>` | List resources recursively under a tag |
| `tag-tags` | `<resource>` | Show referring tag directories as a tree |
| `tag-orphans` | none | List immediate resources without tag links |
| `tag-mv` | `<old> <new>` | Move a resource and update its links |
| `tag-rm` | `<resource> [<tag>...]` | Remove links from named tags, or ask before removing all |
| `tag-fix` | none | Ask before deleting broken links and stray tag files |

Bare tags in `tag-query` are ANDed; `+` switches following tags to OR and `-`
switches following tags to NOT, until another switch appears. Tag arguments are
paths such as `tag/music`. Inputs can be relative to the current directory or
absolute. With OR tags, the candidates are their union; otherwise the first AND
tag supplies the candidates. All AND tags then restrict the candidates, and NOT
tags exclude resources. Explicit tags define the search scope, including tags
outside the library. Without AND or OR tags, candidates come from the entire
library tag tree. Unrelated tags are not scanned; errors in scanned tags are
reported. Results are deduplicated and displayed in path order.

The commands target systems with shell and symbolic-link support;
Windows-specific symlink differences are not handled specially.

Interactive commands accept only lowercase `y`; EOF cancels. With named tags,
`tag-rm` recursively removes links targeting the resource under those tags.
Without named tags, it displays referring tag directories and asks before
removing the links. The resource itself is left untouched. `tag-tags` and
interactive `tag-rm` render sorted trees in Python.

`tag-orphans` considers only immediate children of `res/`. `tag-fix` first offers
to remove broken links, then stray files in the tag tree; permission errors
are reported rather than classified as broken links.

`tag-mv` updates tag entry names to match the moved resource and uses the actual
destination when moving into a directory. Conflicting tag entry names are
checked before the move. Moving a resource directory does not update references
to resources inside it. Moves and link updates are not transactional.

## License

MIT. See [LICENSE](LICENSE).

Output paths are relative to TAG_ROOT. The list command runs in TAG_ROOT.

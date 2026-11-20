# tag

A Python command-line tool for tagging files and directories. Real resources stay
in `res/`; each tag is a directory of relative symlinks pointing at them. Tags
can be nested, and a resource can belong to several tags.

## Setup

The project requires the Python version declared in `.python-version`.
There are no third-party runtime Python dependencies. For development and a
personal isolated installation, uv can be used:

```sh
uv sync --group build
uv tool install .
```

The installation provides `tag-add`, `tag-query`, `tag-ls`, `tag-tags`,
`tag-orphans`, `tag-mv`, `tag-rm`, and `tag-fix`.
`make` (or `make all`) builds a source distribution and wheel in `dist/`;
the selected Python must have `build` and the `uv_build` backend installed.
Builds use `--no-isolation` and do not install build dependencies automatically.
The `build` dependency group declares these tools and `installer`. To build
with the project environment explicitly, run `make PYTHON=.venv/bin/python`.
`make clean` removes those package archives. `make install` builds first, then
installs the wheel using `python -m installer`. The selected Python must have
the `installer` module available; this is an installation tool dependency,
not a runtime dependency. `PREFIX` defaults to `/usr/local`. Python determines
the module and executable directory layout; `PYTHON` and `DISTDIR` can
also be overridden.

On Arch Linux, the build and installation tools are provided by `python-build`,
`python-installer`, and `python-uv-build`; runtime requires `python>=3.14`.

`DESTDIR` defaults to empty and can stage files for packaging:

```sh
make install PREFIX=/usr DESTDIR="$PWD/pkg" PYTHON=/usr/bin/python
```

Files are written under `pkg/usr/`, while launchers use the selected Python
interpreter rather than the staging directory. Use the intended runtime
interpreter when packaging; an interpreter from a development virtual environment
would bind launchers to that environment. The final module directory must be
on that interpreter's import path. For a personal isolated installation, use
`uv tool install .` as shown above.

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

File lists show paths relative to the current working directory, and `TAG_LISTER`
runs in that directory. Tag trees remain relative to the library root.

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

`tag-add` prints a tree of the affected tags and their parent directories,
marking newly created directories with `+` immediately after the tree branch
and leaving existing directories unmarked. Each added link is shown as
`name -> target`. Link targets are relative to the containing tag directory;
the tree is relative to the library root. Unrelated tags are omitted.

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

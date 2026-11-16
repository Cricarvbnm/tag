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

The installation provides eight separate commands: `tag-add`, `tag-rm`,
`tag-mv`, `tag-fix`, `tag-ls`, `tag-tags`, `tag-orphans`, and `tag-query`.
`make install PREFIX="$HOME/.local"` installs them under the selected prefix.

## Library root and configuration

A library contains fixed `res/` and `tag/` directories. If `TAG_ROOT` is set,
that directory must contain both directories or the command reports an error.
Otherwise, commands search upward from the current directory and use the first
matching ancestor. If none exists, the same root error is reported.

`TAG_LISTER` configures the external command used for ordinary file lists. It
defaults to `ls -1`; the command is split on spaces and receives `-d` followed by
the paths. `tag-tags` and interactive `tag-rm` render a sorted plain-text tree
in Python and do not need the external `tree` program.

## Commands

| Command | Arguments | Purpose |
| --- | --- | --- |
| `tag-add` | `<resource> <tag>...` | Link a resource into tags |
| `tag-rm` | `<resource> [<tag>...]` | Interactively remove links, or remove from named tags |
| `tag-mv` | `<old> <new>` | Move a resource and repoint its links |
| `tag-fix` | none | Interactively delete broken links and stray files |
| `tag-ls` | `<tag>` | List resources in a tag recursively |
| `tag-tags` | `<resource>` | Show the resource's tag directories as a tree |
| `tag-orphans` | none | List top-level resources without tag links |
| `tag-query` | `[tags...]` | Filter resources by tag expressions |

Bare tags in `tag-query` are ANDed; `+` switches following tags to OR and `-`
switches following tags to NOT, until another switch appears. Tag arguments are
paths such as `tag/music`. Inputs can be relative to the current directory or
absolute. The commands target systems with shell and symbolic-link support;
Windows-specific symlink differences are not handled specially.

## License

MIT. See [LICENSE](LICENSE).

Output paths are relative to TAG_ROOT. The list command runs in TAG_ROOT.

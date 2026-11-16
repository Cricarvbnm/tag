# tag

A fish shell tool that tags files and directories: real files stay in `res/`, and
each tag is a directory of relative symlinks pointing at them.

## Model

```text
library/
├── res/
│   ├── track.flac
│   └── extra.flac
└── tag/
    ├── music/track.flac -> ../../res/track.flac
    └── lossless/track.flac -> ../../res/track.flac
```

- `res/` (`TAG_RES`) holds the real resources; tagging never moves or rewrites them.
- `tag/` (`TAG_DIR`) holds one directory per label, each containing symlinks to
  resources. A resource can belong to many tags, and a tag is a plain directory, so
  nesting such as `tag/music/lossless` works: lookups scan the tag tree recursively.
- Links are created with `ln -srv`, so they are relative to their own location and no
  absolute path is stored in the library.
- Commands that scan the whole library (`tag-fix`, `tag-orphans`, `tag-query`) find
  the root by walking up from `$PWD` to the first directory containing both `res/`
  and `tag/`.
- The checkout's `.gitignore` lists `res/` and `tag/`.

## Requirements

- fish shell; all commands share `tag-common.fish`.
- GNU coreutils and findutils: `readlink`, `realpath` (needs `-s` and
  `--relative-base`), `find` (needs `-xtype`), `sort`, `comm`, `mktemp`, `ls`, `ln`,
  `mkdir`, `rm`, `mv`, `dirname`, `basename`, `cat`, `printf`.
- `tree` for `tag-tags` and the interactive `tag-rm` (`tree --fromfile`); `install`
  and GNU `sed -i` for `make install`.

## Installation

A clone is usable directly, since every command sources `tag-common.fish` beside it —
there is no build step. Put the clone on `PATH` to use the commands from anywhere:

```fish
git clone <repository-url> ~/src/tag
set -x PATH ~/src/tag $PATH   # add to config.fish to persist
```

Or run `make install`: it defaults to `PREFIX=/usr/local`, honours
`DESTDIR`, installs the eight commands into `$(PREFIX)/bin` (mode 755) and
`tag-common.fish` into `$(PREFIX)/share/tag` (mode 644), and rewrites the commands'
`source` line to that library path, so installed copies depend on the prefix
recorded at install time.

```bash
make install PREFIX=$HOME/.local
make uninstall PREFIX=$HOME/.local
```

## Getting started

```fish
mkdir -p ~/library/res ~/library/tag && cd ~/library
cp ~/Music/track.flac res/
tag-add res/track.flac tag/music tag/lossless   # ln -v: 'tag/music/track.flac' -> '../../res/track.flac'
tag-ls tag/music                                # res/track.flac
tag-query tag/music tag/lossless                # res/track.flac
cp ~/Music/extra.flac res/ && tag-orphans       # res/extra.flac
```

## Commands

| Command | Arguments | Purpose |
| --- | --- | --- |
| [tag-add](tag-add) | `<resource> <tag>...` | Link a resource into tags |
| [tag-rm](tag-rm) | `<resource> [<tag>...]` | Remove links |
| [tag-mv](tag-mv) | `<old> <new>` | Move a resource and repoint its links |
| [tag-fix](tag-fix) | none | Delete broken links and stray files |
| [tag-ls](tag-ls) | `<tag>` | List the resources of a tag |
| [tag-tags](tag-tags) | `<resource>` | List the tags of a resource |
| [tag-orphans](tag-orphans) | none | List resources no tag links to |
| [tag-query](tag-query) | `[tags...]` | Filter resources by tag expressions |

### tag-add

`tag-add <resource> <tag>...` takes at least two arguments. For each tag it runs
`mkdir -p` and links the resource with `ln -srv` (symbolic, relative, verbose). Tag
arguments are used as given — nothing is prefixed, so from the library root pass
`tag/<label>`. The script does not check the resource; `ln` reports a failure.

```fish
tag-add res/track.flac tag/music tag/lossless
```

### tag-rm

`tag-rm <resource>` is interactive: it lists the tag directories linking to the
resource as a tree, prompts `确认删除以上所有的资源的标签? [y/N] `, and removes those
links only when the answer is exactly lowercase `y` (`Y` and an empty answer delete
nothing) — never the resource or the tag directories; no links means no output and
exit 0. `tag-rm <resource> <tag>...` removes
`<tag>/<basename of resource>` for each named tag with `rm -v`, without confirmation.

```fish
tag-rm res/track.flac tag/music tag/temp
```

### tag-mv

`tag-mv <old> <new>` takes exactly two arguments. It collects the links pointing at
`<old>`, runs `mv <old> <new>`, then replaces each link with a fresh relative link to
`<new>` in the same tag directory. An untagged resource is just moved.

### tag-fix

`tag-fix` takes no arguments and scans `$TAG_ROOT/$TAG_DIR` twice: broken symlinks
(`find ... -xtype l`) and stray entries that are neither symlinks nor directories
(`find ... ! -type l ! -type d`). Each group is listed, prompted, and deleted only on
the answer `y` — it repairs nothing, a link to a moved file is deleted, not recreated.

### tag-ls

`tag-ls <tag>` takes exactly one argument and prints the link targets of `<tag>` made
relative to `$PWD`, sorted and deduplicated, through `$TAG_LISTER`, e.g.
`tag-ls tag/music` prints `res/track.flac`. An empty tag prints nothing and exits 0; a
missing tag directory is an error on stderr with exit 1.

### tag-tags

`tag-tags <resource>` takes exactly one argument and is the reverse lookup of
`tag-ls`: it finds every link whose target resolves to the resource and prints the
containing tag directories as a tree (`tree --fromfile`), e.g. `tag-tags res/track.flac`.
No matches print nothing and exit 0; a missing resource is an error on stderr, exit 1.

### tag-orphans

`tag-orphans` takes no arguments. It compares the top-level entries of
`$TAG_ROOT/$TAG_RES` with every path linked from under `$TAG_ROOT/$TAG_DIR` and prints
the difference through `$TAG_LISTER`. Only top-level entries of `res/` are considered:
files inside its subdirectories are neither linked nor reported as orphans.

### tag-query

Bare tags in `tag-query [tags...]` are ANDed; a `+` switches the following tags to OR
and a `-` to NOT, and the mode holds until the next switch. Candidates are the union
of the OR tags when any are given, otherwise every tagged resource; each AND tag is
intersected and each NOT tag subtracted. A `+` therefore changes the starting set,
not the AND constraints: `tag-query tag/music + tag/live` means `music AND live`,
while `tag-query + tag/music tag/live` (no AND tags) is their union. Only tagged
resources are ever returned. No arguments prints every tagged resource and exits 0; a
tag that is not a directory is reported on stderr with exit 1 before filtering.

```fish
tag-query tag/music                     # all music
tag-query tag/music tag/lossless        # in both
tag-query + tag/music tag/live          # in either
tag-query tag/music - tag/lossless      # music but not lossless
```

## Configuration

Defaults come from [tag-common.fish](tag-common.fish) and are only applied to
variables that are not already set, so exported values win.

| Variable | Default | Meaning |
| --- | --- | --- |
| `TAG_ROOT` | `$PWD` | Directory containing `res/` and `tag/` |
| `TAG_RES` | `res` | Name of the resource directory |
| `TAG_DIR` | `tag` | Name of the tag directory |
| `TAG_LISTER` | `ls -1` | Command printing file lists; split on spaces and called with `-d` before the paths |

If `$TAG_ROOT/$TAG_RES` or `$TAG_ROOT/$TAG_DIR` is not a directory, `TAG_ROOT` is then
set to the first directory found by walking up from `$PWD` that contains both, falling
back to `$PWD`; a `TAG_ROOT` without both directories is thus ignored.

## Conventions

- `tag-ls` and `tag-tags` print no output and exit 0 on an empty result, per the
  header of [tag-common.fish](tag-common.fish).
- `tag-orphans` and `tag-query` do not guard the empty case: with no matching
  resources they call the lister with no arguments, and the default `ls -1 -d` then
  prints `.`. Expect that lone dot rather than silence (a known rough edge).
- Errors go to stderr and exit 1 (`die` in `tag-common.fish`); a wrong argument count
  prints a usage line such as `用法: <tag>` and exits 1.
- Inputs are paths relative to `$PWD` or absolute paths, and output is made relative
  to `$PWD` where possible (`realpath -s --relative-base $PWD`); `$PWD` need not be
  the library root.
- Tag arguments are directory paths, not names resolved against
  `$TAG_ROOT/$TAG_DIR`; lookup commands require them to exist and `tag-add` creates
  them, so from the library root a tag is written `tag/<label>`.
- Paths containing spaces are unsupported: the scripts expand variables unquoted in
  calls such as `find $TAG_ROOT/$TAG_DIR` and `mkdir -p $tag`.
- Only `tag-add` creates directories (the tags it is given); `res/` and `tag/` must
  already exist.

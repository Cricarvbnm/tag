.DEFAULT_GOAL := all

PREFIX ?= /usr/local
DESTDIR ?=
DISTDIR ?= dist
PYTHON ?= python
VERSION = $(shell $(PYTHON) -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')
WHEEL = $(DISTDIR)/tag-$(VERSION)-py3-none-any.whl

.PHONY: all build install clean

all: build

build:
	"$(PYTHON)" -m build --no-isolation --outdir "$(DISTDIR)"

install: all
	"$(PYTHON)" -m installer --prefix="$(PREFIX)" $(if $(DESTDIR),--destdir="$(DESTDIR)") --overwrite-existing "$(WHEEL)"

clean:
	$(RM) -- "$(DISTDIR)"/tag-*.whl "$(DISTDIR)"/tag-*.tar.gz

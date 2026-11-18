.DEFAULT_GOAL := all

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
TOOL_DIR ?= $(PREFIX)/lib/uv/tools
DISTDIR ?= dist
UV ?= uv
PYTHON ?= python
VERSION = $(shell $(PYTHON) -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')
WHEEL = $(DISTDIR)/tag-$(VERSION)-py3-none-any.whl

.PHONY: all build install clean

all: build

build:
	$(UV) build --python "$(PYTHON)" --out-dir "$(DISTDIR)"

install: all
	UV_TOOL_DIR="$(TOOL_DIR)" UV_TOOL_BIN_DIR="$(BINDIR)" $(UV) tool install --python "$(PYTHON)" --force "$(WHEEL)"

clean:
	$(RM) -- "$(DISTDIR)"/tag-*.whl "$(DISTDIR)"/tag-*.tar.gz

PREFIX ?= /usr/local
COMMANDS = tag-add tag-fix tag-ls tag-mv tag-orphans tag-query tag-rm tag-tags

.PHONY: install uninstall

install:
	uv tool install --force --prefix "$(DESTDIR)$(PREFIX)" .

uninstall:
	uv tool uninstall --prefix "$(DESTDIR)$(PREFIX)" tag
	 rm -f $(addprefix $(DESTDIR)$(PREFIX)/bin/,$(COMMANDS))

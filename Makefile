PREFIX ?= /usr/local
BINDIR  = $(PREFIX)/bin
DATADIR = $(PREFIX)/share/tag

SCRIPTS = tag-add tag-fix tag-ls tag-mv tag-orphans tag-query tag-rm tag-tags

.PHONY: install uninstall

install:
	install -d $(DESTDIR)$(BINDIR) $(DESTDIR)$(DATADIR)
	install -m 755 $(SCRIPTS) $(DESTDIR)$(BINDIR)/
	sed -i 's|source (dirname (status filename))/tag-common.fish|source $(DATADIR)/tag-common.fish|' \
		$(addprefix $(DESTDIR)$(BINDIR)/,$(SCRIPTS))
	install -m 644 tag-common.fish $(DESTDIR)$(DATADIR)/

uninstall:
	rm -f $(addprefix $(DESTDIR)$(BINDIR)/,$(SCRIPTS))
	rm -rf $(DESTDIR)$(DATADIR)

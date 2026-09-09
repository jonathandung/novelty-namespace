SPHINXOPTS ?=
SPHINXBUILD ?= sphinx-build
.PHONY: help Makefile
.SILENT:
help:
	"$(SPHINXBUILD)" -M help source build $(SPHINXOPTS) $(O)
%: Makefile
	"$(SPHINXBUILD)" -M "$@" source build $(SPHINXOPTS) $(O)

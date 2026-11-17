author = "Jonathan Dung"
copyright = "2026 Jonathan Dung"  # ruff: ignore[builtin-variable-shadowing]
extensions = [
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]
html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/jonathandung/novelty-namespace",
    "source_branch": "main",
    "source_directory": "docs/source/",
    "top_of_page_buttons": ["view", "edit"],
}
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
napoleon_google_docstring = True
needs_sphinx = "9.2.0"
nitpicky = True
project = "novelty-namespace"
pygments_style = "sphinx"
release = "0.4.0"
html_short_title = f"{project} {release} docs"
version = "0.4"

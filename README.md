# bluesky.github.io docs

This repository is the GitHub Pages site for the Bluesky Project. Most project
documentation here is **built output** from other repositories, not source that
should be edited directly.

## What Should I Edit?

Edit this repository only for content owned by the site itself, such as:

```text
index.html
_assets/
matrix/
status/
events/
CNAME
.nojekyll
```

Do not normally edit generated documentation files here, including:

```text
*.html
_sources/*.txt
_static/*
searchindex.js
.doctrees/
objects.inv
```

For project docs, edit the upstream project repository instead. For example, the
Bluesky tutorial source is in:

```text
https://github.com/bluesky/bluesky
docs/tutorial.rst
```

## Why?

GitHub Pages serves static files. Sphinx documentation must be built into HTML,
assets, search indexes, and source-view files before it can be published.

Some Bluesky projects build docs in their own repositories and push the built
files into this repository under a project directory such as `tiled/` or
`bluesky-queueserver/`.

Other projects may publish elsewhere. For example, current `bluesky/bluesky`
docs publish to that repository's own `gh-pages` branch and are served under:

```text
https://blueskyproject.io/bluesky/main/
```

This means generated files in this repository can be legacy output or be
overwritten by the next docs deployment.

## Building Bluesky Docs Locally

For example the Bluesky tutorial, **don't edit this repo**, instead:

```bash
git clone https://github.com/bluesky/bluesky.git
cd bluesky
python -m pip install -e ".[dev]"
tox -e docs
```

The built docs are written to:

```text
build/html/
```

Preview them with:

```bash
cd build/html
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/tutorial.html
```

## Rule of Thumb

If the page belongs to a project package, edit that package's source repository.
If the page is part of the shared landing site or local community pages, edit
this repository.

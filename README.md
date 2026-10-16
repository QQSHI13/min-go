# minify-go

Python wheels for [tdewolff/minify](https://github.com/tdewolff/minify) (the Go
minifier) under our own PyPI namespace, built by GitHub Actions.

Why this repo exists:

- The official `tdewolff-minify` release on PyPI lags the upstream Go library
  (we build the current upstream tag) and ships **no macOS arm64 wheels**.
- A nightly cron builds the latest upstream **release tag** and publishes the
  wheels automatically. No code is maintained here; the wheels are built from
  pinned upstream tags with pinned toolchain versions (see
  `.github/workflows/release.yml`).

## Install

```bash
pip install minify-go
```

The Python module is `minify` (kept identical to upstream's binding):

```python
import minify

m = minify.config({})
html = m.string("text/html", "<div>  hello </div>")
css = m.string("text/css", "body { color: red; }")
js = m.string("application/javascript", "var x = 1;")
```

## Wheels

| Platform | Arch | Runner |
|----------|------|--------|
| Linux (manylinux) | x86_64, aarch64 | ubuntu-latest / ubuntu-24.04-arm |
| macOS | x86_64, arm64 | macos-15-large / macos-15 |
| Windows | amd64 | windows-latest |

Python 3.10 - 3.14.

## How it works

1. A scheduled workflow (daily 02:00 UTC, or manual `workflow_dispatch`)
   queries the latest `vX.Y.Z` tag of `tdewolff/minify`.

   Note: musllinux wheels are not built - Go `c-shared` libraries cannot be
   dlopen'd on musl (initial-exec TLS relocation error), so Alpine Linux is
   unsupported by the Go binding itself.
2. If that tag was already built (GitHub Actions cache), the run stops.
3. Otherwise the upstream tag is checked out, the PyPI project name in
   `bindings/py/setup.py` is renamed to `minify-go`, and cibuildwheel builds all
   wheels (the Go extension is compiled with `make -C bindings/py compile`,
   same as upstream).
4. Each wheel is smoke-tested in a fresh venv (`smoke.py`).
5. Wheels are published to PyPI via trusted publishing (OIDC) — no tokens.

Version numbers mirror the upstream tag (e.g. `2.24.17`).

## Known issues

- **Windows: possible segfault while the DLL unloads at interpreter exit.**
  Go's runtime cannot reliably unload a `c-shared` library
  ([golang/go#11100](https://github.com/golang/go/issues/11100)), so on Windows a
  process that has imported `minify` can crash *after* its minification work has
  completed. Measured on `windows-2025-vs2026`: **3 of 12** bare `import minify`
  runs exited with a segfault, identically for 2.24.20 and 2.24.21; Linux and
  macOS were clean (0 of 12). The crash is version-independent and pre-existing,
  so CI tolerates it only when `smoke.py` has already printed its success
  sentinel — a crash before the assertions pass still fails the build.
  Practical impact: output is always correct, but a Windows process may exit
  non-zero. A subprocess-based binding (running the Go minifier out-of-process)
  is the durable fix and is not implemented yet.

## Maintenance

- Bump `GO_VERSION` and the Go tarball URLs in the workflow when upstream
  requires a newer Go.
- Dependabot keeps the pinned GitHub Actions at the latest versions.

## License

The wheels embed code from `tdewolff/minify`, Copyright (c) Taco de Wolff,
MIT licensed. See `NOTICE`.
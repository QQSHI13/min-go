"""Smoke test for the min-go wheels.

Installed in a fresh venv by CI after building; asserts the minify behaviors
DocsForge relies on:
- SVG viewBox / preserveAspectRatio survive HTML minification
- CSS data-URI backgrounds survive CSS minification
- JavaScript is parse-based minified
"""

import minify


def main() -> None:
    m = minify.config({})

    html = '<svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet"><path d="M0 0"/></svg>'
    out = m.string("text/html", html)
    assert "viewBox" in out and "preserveAspectRatio" in out, out

    css = "body { background: url(data:image/png;base64,iVBORw0KGgo=); }"
    out = m.string("text/css", css)
    assert "data:image" in out, out

    js = "var x = 1; var y = 2;"
    out = m.string("application/javascript", js)
    assert "var x=1,y=2" in out, out

    print("smoke ok:", out)


if __name__ == "__main__":
    main()
# Fishwrap brand assets

The brand assets — wordmark, favicon, Open Graph card — are produced from
the live font using `fontTools` and ImageMagick. No generative AI is used in
the pipeline. The thesis of the engine is that the algorithm is readable;
the brand assets are produced the same way.

## Reproducing the assets

Requirements:

- `fontTools` (Python). Install via `pipx install fonttools` and point at
  the pipx venv's Python, or `pip install fonttools` in a venv.
- ImageMagick on `$PATH`, providing the `magick` command.

The fonts ship with the repo under `docs/static/fonts/`:

- `LibreBaskerville-variable.ttf` (SIL OFL)
- `LibreBaskerville-Italic-variable.ttf` (SIL OFL)
- `iAWriterMonoS-Regular.ttf` (SIL OFL)
- `iAWriterMonoS-Italic.ttf` (SIL OFL)

Run from this directory:

```bash
~/.local/pipx/venvs/fonttools/bin/python generate-assets.py
```

Or activate a venv with `fontTools` installed and run `python generate-assets.py`.

The script writes:

- `docs/static/images/fishwrap_logo.svg` — path-only wordmark SVG
- `docs/static/images/favicon.svg` — path-only pilcrow glyph
- `docs/static/images/favicon-{16,32,48,64,96,128,180,192,256,512}.png`
- `docs/favicon.ico` — multi-resolution legacy ICO at site root
- `docs/static/images/og-card.png` — 1200×630 Open Graph card

See `docs/BRAND.md` §6 for the spec the assets implement and §7 for the
production method.

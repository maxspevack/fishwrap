#!/usr/bin/env python3
"""
Fishwrap brand asset generator.

Produces the wordmark, favicon set, and Open Graph card from Libre Baskerville
and iA Writer Mono. Path-only SVGs (no font dependency at render time) plus
ImageMagick-rasterized PNG fallbacks.

Run from any directory; paths resolve relative to this script.

Requirements:
  - fontTools (pip install fonttools, or pipx install fonttools then point at
    the pipx venv's python)
  - ImageMagick on PATH (provides the `magick` command)
"""
import subprocess
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

SCRIPT_DIR = Path(__file__).resolve().parent
FONTS_DIR = SCRIPT_DIR.parent / "fonts"
IMAGES_DIR = SCRIPT_DIR.parent / "images"
SITE_ROOT = SCRIPT_DIR.parent.parent  # docs/

LIBRE_BASKERVILLE = FONTS_DIR / "LibreBaskerville-variable.ttf"
LIBRE_BASKERVILLE_ITALIC = FONTS_DIR / "LibreBaskerville-Italic-variable.ttf"
IA_WRITER_MONO = FONTS_DIR / "iAWriterMonoS-Regular.ttf"

WORDMARK_TEXT = "Fishwra¶"  # ¶ = ¶ PILCROW SIGN
WEIGHT_BOLD = 700

INK = "#0E0D0C"        # Refusal Black
PAPER = "#EBE6DC"      # Smoke Cream
MARGIN = "#5C5247"     # Margin Ink
PENCIL = "#9C1B14"     # Cardinal Red — the editor's pencil

# Per-character color overrides for the wordmark. Default (any character not
# named here) is INK. Indices match WORDMARK_TEXT character positions.
WORDMARK_COLORS = {7: PENCIL}  # index 7 = the pilcrow

FAVICON_SIZES = [16, 32, 48, 64, 96, 128, 180, 192, 256, 512]
ICO_SIZES = [16, 32, 48]


def instance_font(path: Path, weight: int) -> TTFont:
    """Open a variable font and instance the weight axis."""
    font = TTFont(str(path))
    return instantiateVariableFont(font, {"wght": weight})


def glyph_path_d(glyph_set, glyph_name: str) -> tuple[str, int]:
    """Return (SVG path 'd' attribute, advance width in font units)."""
    pen = SVGPathPen(glyph_set)
    glyph = glyph_set[glyph_name]
    glyph.draw(pen)
    return pen.getCommands(), glyph.width


def generate_wordmark():
    """Produce fishwrap_logo.svg from the wordmark text."""
    font = instance_font(LIBRE_BASKERVILLE, WEIGHT_BOLD)
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()
    ascent = font["OS/2"].sTypoAscender
    descent = font["OS/2"].sTypoDescender

    paths = []
    x_cursor = 0
    for idx, ch in enumerate(WORDMARK_TEXT):
        gname = cmap.get(ord(ch))
        if gname is None:
            sys.exit(f"No glyph for {ch!r} (U+{ord(ch):04X}) in {LIBRE_BASKERVILLE.name}")
        path_d, advance = glyph_path_d(glyph_set, gname)
        color = WORDMARK_COLORS.get(idx, INK)
        if path_d:
            paths.append((x_cursor, path_d, gname, color))
        x_cursor += advance

    wm_width = x_cursor
    wm_height = ascent - descent  # descent is negative

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-ascent} {wm_width} {wm_height}" preserveAspectRatio="xMidYMid meet">',
        '  <g transform="scale(1,-1)">',
    ]
    for x, d, gname, color in paths:
        svg_lines.append(f'    <path transform="translate({x},0)" d="{d}" fill="{color}"/>  <!-- {gname} -->')
    svg_lines.append("  </g>")
    svg_lines.append("</svg>\n")

    out = IMAGES_DIR / "fishwrap_logo.svg"
    out.write_text("\n".join(svg_lines))
    print(f"  wordmark SVG: {out}")
    return out


def generate_favicon():
    """Produce favicon.svg and the PNG raster set."""
    font = instance_font(LIBRE_BASKERVILLE, WEIGHT_BOLD)
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()

    pilcrow_gname = cmap[ord("¶")]
    path_d, _ = glyph_path_d(glyph_set, pilcrow_gname)

    # Compute tight bounds of the pilcrow glyph
    bounds_pen = BoundsPen(glyph_set)
    glyph_set[pilcrow_gname].draw(bounds_pen)
    xmin, ymin, xmax, ymax = bounds_pen.bounds
    p_width = xmax - xmin
    p_height = ymax - ymin

    # Square canvas, 1.6x the larger glyph dimension for breathing room
    canvas = int(max(p_width, p_height) * 1.6)
    offset_x = (canvas - p_width) / 2 - xmin
    offset_y = (canvas - p_height) / 2 + ymax

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas} {canvas}" preserveAspectRatio="xMidYMid meet">\n'
        f'  <rect width="{canvas}" height="{canvas}" fill="{PAPER}"/>\n'
        f'  <g transform="translate({offset_x},{offset_y}) scale(1,-1)" fill="{INK}">\n'
        f'    <path d="{path_d}"/>\n'
        f"  </g>\n"
        f"</svg>\n"
    )

    svg_out = IMAGES_DIR / "favicon.svg"
    svg_out.write_text(svg)
    print(f"  favicon SVG: {svg_out}")

    # Rasterize PNGs at every size
    png_paths = {}
    for size in FAVICON_SIZES:
        png_out = IMAGES_DIR / f"favicon-{size}.png"
        subprocess.run(
            [
                "magick", "-background", PAPER, "-density", "600",
                str(svg_out), "-resize", f"{size}x{size}", "-strip",
                str(png_out),
            ],
            check=True,
        )
        png_paths[size] = png_out
        print(f"  favicon-{size}.png")

    # Multi-resolution ICO at the site root (legacy fallback)
    ico_out = SITE_ROOT / "favicon.ico"
    subprocess.run(
        ["magick"] + [str(png_paths[s]) for s in ICO_SIZES] + [str(ico_out)],
        check=True,
    )
    print(f"  favicon.ico (16+32+48): {ico_out}")


def generate_og_card():
    """Produce og-card.png by compositing the wordmark + tagline + edition line."""
    wordmark_svg = IMAGES_DIR / "fishwrap_logo.svg"
    if not wordmark_svg.exists():
        sys.exit("wordmark SVG not found; run generate_wordmark first")

    # Render wordmark to a PNG at OG card target height (150 pixels tall)
    wm_og = IMAGES_DIR / "_og-wordmark.png"
    subprocess.run(
        [
            "magick", "-background", PAPER, "-density", "600",
            str(wordmark_svg), "-resize", "x150",
            str(wm_og),
        ],
        check=True,
    )

    # Build base canvas with text annotations
    base = IMAGES_DIR / "_og-base.png"
    subprocess.run(
        [
            "magick", "-size", "1200x630", f"xc:{PAPER}",
            "-font", str(LIBRE_BASKERVILLE_ITALIC),
            "-pointsize", "26", "-fill", MARGIN, "-gravity", "north",
            "-annotate", "+0+260", "The peasants scroll. The elite read.",
            "-font", str(IA_WRITER_MONO),
            "-pointsize", "22", "-fill", INK, "-gravity", "center",
            "-annotate", "+0+80",
            "edition 0142  ·  6 sections  ·  41 articles  ·  the back page is page 11",
            "-pointsize", "16", "-fill", MARGIN, "-gravity", "southeast",
            "-annotate", "+56+40", "fishwrap.org",
            str(base),
        ],
        check=True,
    )

    # Composite the wordmark onto the canvas
    prerule = IMAGES_DIR / "_og-prerule.png"
    subprocess.run(
        [
            "magick", str(base), str(wm_og),
            "-gravity", "north", "-geometry", "+0+100",
            "-composite", str(prerule),
        ],
        check=True,
    )

    # Draw the rule between wordmark and tagline
    out = IMAGES_DIR / "og-card.png"
    subprocess.run(
        [
            "magick", str(prerule),
            "-fill", MARGIN, "-draw", "rectangle 360,230 840,231",
            str(out),
        ],
        check=True,
    )

    # Clean up intermediates
    for tmp in (wm_og, base, prerule):
        tmp.unlink()

    print(f"  OG card: {out}")


def main():
    print("Generating Fishwrap brand assets")
    print(f"  fonts dir : {FONTS_DIR}")
    print(f"  images dir: {IMAGES_DIR}")
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    generate_wordmark()
    generate_favicon()
    generate_og_card()
    print("done.")


if __name__ == "__main__":
    main()

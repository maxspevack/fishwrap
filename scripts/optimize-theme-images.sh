#!/usr/bin/env bash
#
# Regenerate AVIF + WebP + downscaled PNG/JPG fallbacks from source images.
#
# Reads sources from each theme's sources/ directory (deliberately outside
# static/ so demos.yml's cp -r static/. does not deploy them) and writes
# derivatives into static/images/.
#
# Required tools: cwebp, avifenc, sips (macOS) or magick (Linux fallback).
# All three available via Homebrew on macOS; libwebp + libavif + imagemagick
# on Linux.
#
# Re-run this any time you change a source image. Output files are tracked
# in git so the build does not depend on the tools being present in CI.

set -euo pipefail

# Run from repo root.
cd "$(dirname "$0")/.."

# WebP / AVIF target width for hero images. 1600 keeps retina headroom
# (section-hero displays at 300px tall, ~1100px wide).
HERO_VECTOR_WIDTH=1600
# PNG fallback width. Don't upscale past the source — PNG can't compress
# away the upscaled pixels.
HERO_PNG_WIDTH=1024
# Logo dimensions. Rendered at 180x180 (max-width); 360 = 2x retina.
LOGO_VECTOR_WIDTH=360
LOGO_PNG_WIDTH=360

# Quality knobs. AVIF q ~ 60 is visually lossless for graphic content;
# WebP q ~ 80 is a long-standing default.
AVIF_Q=60
WEBP_Q=80

size() { stat -f%z "$1" 2>/dev/null || stat -c%s "$1"; }

emit_variants() {
    local src="$1" stem="$2" vector_width="$3" fallback_width="$4" fallback_kind="$5" out_dir="$6"

    local out_fallback
    if [ "$fallback_kind" = "jpg" ]; then
        out_fallback="${out_dir}/${stem}.jpg"
        magick "$src" -resize "${fallback_width}x${fallback_width}>" -strip -quality 82 "$out_fallback"
    else
        out_fallback="${out_dir}/${stem}.png"
        magick "$src" -resize "${fallback_width}x${fallback_width}>" -strip "$out_fallback"
    fi

    local out_webp="${out_dir}/${stem}.webp"
    local out_avif="${out_dir}/${stem}.avif"

    cwebp -q "$WEBP_Q" -resize "$vector_width" 0 "$src" -o "$out_webp" >/dev/null 2>&1

    local tmp_for_avif
    tmp_for_avif="$(mktemp -t fwavif).png"
    magick "$src" -resize "${vector_width}x${vector_width}>" -strip "$tmp_for_avif"
    avifenc --min "$AVIF_Q" --max "$AVIF_Q" "$tmp_for_avif" "$out_avif" >/dev/null 2>&1
    rm -f "$tmp_for_avif"

    printf "  %-22s %s %7d B  webp %7d B  avif %7d B\n" \
        "$stem" "$fallback_kind" "$(size "$out_fallback")" "$(size "$out_webp")" "$(size "$out_avif")"
}

echo "showrunner theme:"
# Sources live outside static/ deliberately — demos.yml copies static/.
# recursively, so anything under static/ ends up on fishwrap.org.
sr_src="demo/themes/showrunner/sources"
sr_out="demo/themes/showrunner/static/images"
# Hero images are photographic — JPEG fallback compresses far better than PNG.
emit_variants "${sr_src}/section_procedural.png" "section_procedural" "$HERO_VECTOR_WIDTH" "$HERO_PNG_WIDTH" jpg "$sr_out"
emit_variants "${sr_src}/section_gossip.png"     "section_gossip"     "$HERO_VECTOR_WIDTH" "$HERO_PNG_WIDTH" jpg "$sr_out"
# Logo has transparency / hard edges — keep PNG fallback.
emit_variants "${sr_src}/logo_header.png"        "logo_header"        "$LOGO_VECTOR_WIDTH" "$LOGO_PNG_WIDTH" png "$sr_out"

# Clean up old upscaled PNG outputs from prior runs of this script.
rm -f "${sr_out}/section_procedural.png" "${sr_out}/section_gossip.png"

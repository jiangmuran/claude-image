# Post-processing — compress, resize, convert, combine

Generation is just the start. Most real workflows need to compress for the web, convert format, resize for a specific slot, or combine with other assets. Use these one-liners.

## Inspect

```bash
file image.png                              # type sanity check
identify image.png                          # ImageMagick: dimensions, color profile
sips -g pixelWidth -g pixelHeight img.png   # macOS native, no deps
ls -lh image.png                            # size on disk
```

## Compress (lossless or aggressive)

### PNG (lossless / palette reduction)

Best free tools, in order of effort vs. payoff:

```bash
# pngquant — palette quantization, huge wins for illustrations
brew install pngquant
pngquant --quality=70-90 --strip --output out.png image.png

# oxipng — lossless re-encoding
brew install oxipng
oxipng -o 4 --strip safe image.png

# Combine for max savings
pngquant --quality=70-90 image.png -o tmp.png && oxipng -o 4 --strip safe tmp.png -o final.png
```

### JPEG (lossy, for photos)

```bash
# mozjpeg — best quality at a given size
brew install mozjpeg
cjpeg -quality 82 -optimize -progressive image.png > image.jpg

# Or use sips (no install)
sips -s format jpeg -s formatOptions 82 image.png --out image.jpg
```

### WebP (modern web)

```bash
brew install webp
cwebp -q 85 image.png -o image.webp
# Lossless variant for graphics
cwebp -lossless image.png -o image.webp
```

### AVIF (best modern compression)

```bash
brew install libavif
avifenc --min 28 --max 32 -s 4 image.png image.avif
```

Typical savings on a 1024² illustration:
- PNG → pngquant: 60–80% smaller
- PNG → WebP: 70–85% smaller
- PNG → AVIF: 80–90% smaller (slower encode)

## Resize

```bash
# ImageMagick — most flexible
magick image.png -resize 800x800 -strip out.png
magick image.png -resize 50% out.png
magick image.png -resize 800x800^ -gravity center -extent 800x800 out.png  # crop to square

# sips — macOS native
sips -Z 800 image.png --out out.png        # max dimension 800, preserve aspect
sips -z 600 800 image.png --out out.png    # exactly 600x800 (may distort)

# cwebp / cjpeg also accept --resize / -scale
```

## Convert format

```bash
magick image.png image.jpg
magick image.png image.webp
sips -s format jpeg image.png --out image.jpg
```

## Strip metadata

Generated images are clean, but if combining with photos:

```bash
exiftool -all= image.jpg
magick image.jpg -strip out.jpg
```

## Make a transparent background

If the model gave an opaque background and you need transparent:

```bash
# rembg — neural background removal, very good
pip install rembg
rembg i input.png output.png

# Or generate again with --background transparent
```

## Combine multiple images

### Side-by-side / grid

```bash
# Horizontal strip
magick image1.png image2.png +append strip.png

# Vertical
magick image1.png image2.png -append stack.png

# Grid (2x2)
magick \( image1.png image2.png +append \) \
       \( image3.png image4.png +append \) \
       -append grid.png
```

### Composite (overlay)

```bash
magick base.png overlay.png -gravity center -composite out.png

# With transparency / blend modes
magick base.png overlay.png -compose multiply -composite out.png
```

### Add a colored background to a transparent image

```bash
magick image.png -background "#1a1a2e" -alpha remove -alpha off out.png
```

## Add text (when you need a slide / poster locally)

```bash
magick image.png \
  -gravity center -pointsize 64 -fill white \
  -font "Helvetica-Bold" \
  -annotate 0 "HEADLINE" \
  out.png

# Drop shadow effect
magick image.png \
  \( -size 1024x256 xc:none -font "Helvetica-Bold" -pointsize 80 \
     -fill black -annotate +2+2 "TITLE" \
     -fill white -annotate +0+0 "TITLE" \
  \) -gravity north -geometry +0+50 -composite out.png
```

For Chinese, you'll want a font that ships glyphs:

```bash
magick image.png \
  -font "/System/Library/Fonts/PingFang.ttc" \
  -pointsize 72 -fill white -gravity center \
  -annotate 0 "新春快乐" out.png
```

## Make an animated GIF / MP4 from variants

Generate `-n 4` variants and play them:

```bash
# GIF
magick -delay 80 -loop 0 out-*.png variants.gif

# MP4 (requires ffmpeg)
ffmpeg -framerate 1.25 -pattern_type glob -i 'out-*.png' \
  -c:v libx264 -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
  variants.mp4
```

## Pick the right format for the job

| Use | Format |
|-----|--------|
| Web hero with photographic content | WebP @ 80, AVIF as a `<picture>` fallback source |
| Web hero with flat illustration / few colors | PNG via pngquant, or WebP lossless |
| Email image | JPEG (some clients still don't render WebP cleanly) |
| App icon / logo asset | PNG (and SVG export from a vector tool ideally) |
| PPT / Keynote | PNG (slides handle big files fine) |
| Print-quality poster | PNG at 2048+ resolution; export to PDF in a layout tool |
| Game sprite / asset | PNG with transparency; never JPEG |
| Social media (IG / X) | JPEG or PNG depending on whether transparency matters |

## Quick recipe — "make this web-ready"

```bash
# 1. Pick target dimensions
magick generated.png -resize 1600x -strip web-resized.png
# 2. Compress
pngquant --quality=70-90 --strip web-resized.png -o web-final.png
# 3. Also produce WebP & AVIF for a <picture>
cwebp -q 82 web-resized.png -o web-final.webp
avifenc --min 28 --max 32 web-resized.png web-final.avif
```

## Don't bother

- Re-running through 5 compression tools sequentially — diminishing returns and quality loss.
- Converting PNG → JPG → PNG → WebP — every lossy hop costs quality.
- Compressing what you'll regenerate anyway.

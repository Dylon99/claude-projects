# Photography site

Static, dependency-free portfolio: hero image, filterable masonry gallery,
keyboard/swipe lightbox, about + contact. No build step, no framework, no
third-party scripts. A strict CSP is set in `index.html`.

```
index.html          page shell
assets/             styles.css, app.js
photos.json         gallery manifest (drives everything)
photos/full|thumbs  processed images (generated)
tools/              build_gallery.py — not deployed
```

Ships with 12 picsum.photos placeholders so it renders out of the box.

## Add your photos

```bash
cd photography-site
python3 -m venv .venv && . .venv/bin/activate
pip install -r tools/requirements.txt

# originals/ is gitignored; subfolder name = category
mkdir -p originals/landscape originals/street
#   ...copy your photos in...

python3 tools/build_gallery.py originals
```

The tool:

- resizes to 2400px (full) and 900px (thumbs) long edge, auto-rotated
- **strips all metadata, including GPS**, from published files
- pulls camera model + year from EXIF into `photos.json`
- replaces the picsum samples (`--keep-samples` to keep them)
- preserves `title`, `alt`, `location`, `category`, `featured` you edit by hand on re-runs

Then edit `photos.json` for titles/alt text, set `"featured": true` on your hero
shot, and update the About text and contact email in `index.html`.

## Preview

```bash
python3 -m http.server 8000 --directory photography-site
```

## Deploy

`.github/workflows/photography-site.yml` deploys to GitHub Pages on push to
`main` (only when `photography-site/**` changes). One-time setup:
**Settings → Pages → Source: GitHub Actions**.

Once you've dropped the placeholders, tighten the CSP `img-src` to `'self'`.

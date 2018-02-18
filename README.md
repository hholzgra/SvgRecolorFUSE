# SvgRecolorFUSE
Use FUSE to provide arbitrary color versions of a single colored SVG

For every file in the `svg` directory there'll be a directory with the same basename in FUSE mount directory. Arbitrary color names or #XXXXXX hex color values can be used to retrieve modified versions of the base SVG with the color *red* replaced with the given color.

E.g. if your `svg` directroy contains a file `base.svg`, then `mnt/base/Blue.svg` will be a virtual file with all values of `Red` (#ff0000) being replaced with `Blue` (#0000ff).

Usage (e.g.):

`./SvgRecolorFUSE.py -o allow_other -o svgdir=$(pwd)/svg/ ./mnt`

Intended purpose: to allow arbitrary marker colors in a Mapnik style processing preprocessed GeoJson exports from umap (http://umap.openstreetmap.fr/)

#!/usr/bin/env python
"""Reconstruct native-space polar angle + eccentricity from resampled Cartesian
(x, y) visual-field coordinate maps.

Used by 3_fsaverage2native.sh for the visualCoord model: x and y are CONTINUOUS
(no 0/360 wrap), so they are resampled fsaverage->native and PA/ecc are computed
here -- the polar-angle 0/360 seam is therefore never interpolated. The native
x/y maps are already in degrees of visual angle, so (unlike
2_inference._reconstruct_coords, which works on normalized predictions) there is
no ECC_MAX scaling here. Convention matches the fsaverage reconstruction:
    ecc = sqrt(x^2 + y^2)
    PA  = atan2(y, x) in degrees, remapped to [0, 360)
"""
import argparse
import numpy as np
import nibabel as nib


def _save_like(vals, template_path, out_path):
    """Write vals into a copy of template_path's GIFTI (same surface/structure)."""
    gii = nib.load(template_path)
    gii.darrays[0].data = np.asarray(vals, dtype=np.float32)
    nib.save(gii, out_path)


def main():
    ap = argparse.ArgumentParser(
        description='Reconstruct native polarAngle + eccentricity from native x/y maps.')
    ap.add_argument('--x', required=True, help='native x coordinate map (.func.gii)')
    ap.add_argument('--y', required=True, help='native y coordinate map (.func.gii)')
    ap.add_argument('--polarangle', required=True, help='output polarAngle map (.func.gii)')
    ap.add_argument('--eccentricity', required=True, help='output eccentricity map (.func.gii)')
    args = ap.parse_args()

    x = np.asarray(nib.load(args.x).agg_data(), dtype=np.float64).ravel()
    y = np.asarray(nib.load(args.y).agg_data(), dtype=np.float64).ravel()

    ecc = np.sqrt(x ** 2 + y ** 2)
    pa = np.degrees(np.arctan2(y, x))
    pa[pa < 0] += 360.0

    _save_like(pa, args.x, args.polarangle)
    _save_like(ecc, args.x, args.eccentricity)
    print('Reconstructed polarAngle + eccentricity from x/y ({} vertices)'.format(x.size))


if __name__ == '__main__':
    main()

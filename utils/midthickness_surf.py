#!/usr/bin/env python
import nibabel as nib
import os.path as osp
import numpy as np
import argparse


def generate_midthickness_surf(args):
    """Generate midthickness surface from white and pial surfaces.
    
    Args:
        args: argparse object with the following attributes:
            path (str): Path to the surface data folder.
            hemisphere (str): Hemisphere to use.
    Returns:
        str: Path to the generated midthickness surface.
    """

    coords = []
    for surface in ['white', 'pial']:
        surf = nib.load(osp.join(args.path, args.hemisphere + '.' + surface + '.gii'))
        coords.append(surf.agg_data('NIFTI_INTENT_POINTSET'))

    mean_coords = np.mean(coords, axis=0)
    surf.agg_data('NIFTI_INTENT_POINTSET')[:] = mean_coords
    # The image object was loaded from the pial surface; relabel its metadata so
    # the saved file does not claim to be a pial surface (coordinates are already
    # the white/pial average).
    pointset_intent = nib.nifti1.intent_codes['NIFTI_INTENT_POINTSET']
    for darray in surf.darrays:
        if darray.intent == pointset_intent:
            meta = dict(darray.meta)
            meta['AnatomicalStructureSecondary'] = 'MidThickness'
            meta['Name'] = args.hemisphere + '.graymid'
            darray.meta = nib.gifti.GiftiMetaData(meta)
    out_path = osp.join(args.path, args.hemisphere + '.graymid.gii')
    nib.save(surf, out_path)
    return print("Midthickness surface saved at " + out_path)
    
def main():
    parser = argparse.ArgumentParser(description='Generation of midthickness surface')
    parser.add_argument('--path', type=str, help='Path to the surface data folder')
    parser.add_argument('--hemisphere', type=str,
                        default='lh', choices=['lh', 'rh'], help='Hemisphere to use')
    args = parser.parse_args()
    generate_midthickness_surf(args)

if __name__ == '__main__':
    main()
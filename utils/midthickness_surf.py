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

    # print(np.shape(coords))
    mean_coords = np.mean(coords, axis=0)
    surf.agg_data('NIFTI_INTENT_POINTSET')[:] = mean_coords
    nib.save(surf, args.path + args.hemisphere + '.graymid.gii')
    return print("Midthickness surface saved at " + args.path + 
                 args.hemisphere + '.graymid.gii')
    
def main():
    parser = argparse.ArgumentParser(description='Generation of midthickness surface')
    parser.add_argument('--path', type=str, help='Path to the surface data folder')
    parser.add_argument('--hemisphere', type=str,
                        default='lh', choices=['lh', 'rh'], help='Hemisphere to use')
    args = parser.parse_args()
    generate_midthickness_surf(args)

if __name__ == '__main__':
    main()
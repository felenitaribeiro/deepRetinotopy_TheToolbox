#!/usr/bin/env python
"""Checkpoint 4.6: side-by-side polar angle maps for 3 subjects.
Top row: 32k sphere (V1-3), original vs new (sphere.reg frame).
Bottom row: native space, step-2 map (MSMAll->native) vs new map back in native.
Writes checks/plots/<sub>.<hemi>.pa.png"""
import os, sys
import numpy as np
import nibabel as nib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import WORK, load_metric, reconstruct, roi_mask, orig_maps

subs = sys.argv[1:] or ['100610', '102311', '102816']
os.makedirs(f'{WORK}/checks/plots', exist_ok=True)
mats = {}

for sub in subs:
    for hemi, H in [('lh', 'L'), ('rh', 'R')]:
        g = f'{WORK}/gii/{sub}'
        roi = roi_mask(hemi)
        sph32 = nib.load(f'{WORK}/templates/S1200.{H}.sphere.32k_fs_LR.surf.gii').darrays[0].data
        o = orig_maps(sub, hemi, mats=mats)
        new = reconstruct(load_metric(f'{g}/targets.{hemi}.32k_spherereg.func.gii'))
        nat = reconstruct(load_metric(f'{g}/targets.{hemi}.native.func.gii'))
        nsr = reconstruct(load_metric(f'{g}/targets.{hemi}.native_spherereg.func.gii'))
        sphnat = nib.load(f'/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/freesurfer/{sub}/surf/{hemi}.sphere.reg.surf.gii').darrays[0].data
        roinat = nib.load(f'{g}/roi.{hemi}.native.func.gii').darrays[0].data > 0.5

        fig, axes = plt.subplots(2, 2, figsize=(10, 10))
        panels = [(axes[0, 0], sph32, roi, o['pa'], 'original 32k (MSMAll frame)'),
                  (axes[0, 1], sph32, roi, new['pa'], 'new 32k (sphere.reg frame)'),
                  (axes[1, 0], sphnat, roinat, nat['pa'], 'native (step 2, from MSMAll)'),
                  (axes[1, 1], sphnat, roinat, nsr['pa'], 'new back in native (sphere.reg)')]
        for ax, sph, m, pa, title in panels:
            mm = m & np.isfinite(pa)
            sc = ax.scatter(sph[mm, 1], sph[mm, 2], c=pa[mm], cmap='hsv', vmin=0, vmax=360, s=3)
            ax.set_title(f'{title} (n={mm.sum()})', fontsize=9)
            ax.set_aspect('equal'); ax.axis('off')
        fig.colorbar(sc, ax=axes, shrink=0.6, label='polar angle (deg)')
        fig.suptitle(f'{sub} {hemi} polar angle, V1-3')
        fig.savefig(f'{WORK}/checks/plots/{sub}.{hemi}.pa.png', dpi=130, bbox_inches='tight')
        plt.close(fig)
        print('wrote', f'{sub}.{hemi}.pa.png')

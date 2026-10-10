#!/usr/bin/env python
"""Assemble the final *_spherereg.mat files, one output file at a time (low memory).

For every map/fit: load the original .mat, replace only the cortical entries of each
participant's field with the reconstructed sphere.reg-frame values, keep subcortical
entries and all CIFTI metadata fields untouched, save under the same variable name as
cifti_<map>[_fitN]_all_spherereg.mat. Myelin comes from the preferred native route
(myelin.<h>.32k_spherereg / myelin_roi.<h>.32k_spherereg).
"""
import os, sys, gc
import numpy as np
import scipy.io as sio
import nibabel as nib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import WORK, CONV, NHEMI, load_metric, reconstruct, VALID_THR

OUT = os.path.join(WORK, 'mat')
os.makedirs(OUT, exist_ok=True)
FIELD = {'polarAngle': 'polarangle', 'eccentricity': 'eccentricity',
         'pRFsize': 'receptivefieldsize'}
RECKEY = {'polarAngle': 'pa', 'eccentricity': 'ecc', 'pRFsize': 'prf'}
subjects = [s.strip() for s in open(f'{WORK}/subjects.txt') if s.strip()]

jobs = []  # (outname, original file, variable, map, fit)
for m in ['polarAngle', 'eccentricity', 'pRFsize']:
    jobs.append((f'cifti_{m}_all_spherereg.mat', f'cifti_{m}_all.mat', f'cifti_{m}', m, 'fit1'))
    for fit in ['fit2', 'fit3']:
        jobs.append((f'cifti_{m}_{fit}_all_spherereg.mat', f'cifti_{m}_{fit}_all.mat',
                     f'cifti_{m}', m, fit))
jobs.append(('cifti_R2_all_spherereg.mat', 'cifti_R2_all.mat', 'cifti_R2', 'R2', 'fit1'))
jobs.append(('cifti_myelin_all_spherereg.mat', 'cifti_myelin_all.mat', 'cifti_myelin',
             'myelin', None))

for outname, inname, var, m, fit in jobs:
    if os.path.exists(os.path.join(OUT, outname)) and os.path.getsize(os.path.join(OUT, outname)) > 10**6:
        print('exists, skip', outname, flush=True)
        continue
    v = sio.loadmat(os.path.join(CONV, inname))[var]
    for sub in subjects:
        g = f'{WORK}/gii/{sub}'
        if m == 'myelin':
            # mat route (32k MSMAll -> native -> 32k sphere.reg): range-bounded by
            # convexity, matches the smoothness class of the original training input.
            # (The native-route map keeps vessel outliers HCP excluded from its own
            # 32k maps: native max ~19 vs 32k max ~3.6 for 100610.)
            arr = v[f'x{sub}_myelinmap'][0, 0]  # (64984,1)
            for hemi, sl in [('lh', slice(0, NHEMI)), ('rh', slice(NHEMI, 2 * NHEMI))]:
                mm = load_metric(f'{g}/myelin_mat.{hemi}.32k_spherereg.func.gii')
                roi = mm['validm']
                good = roi >= VALID_THR
                with np.errstate(divide='ignore', invalid='ignore'):
                    arr[sl, 0] = np.where(good, mm['myelin'] / np.where(roi > 0, roi, np.nan), np.nan)
        else:
            if m == 'R2':
                fieldname, key = f'x{sub}_fit1_r2_msmall', 'r2'
            else:
                fieldname, key = f'x{sub}_{fit}_{FIELD[m]}_msmall', RECKEY[m]
            arr = v[fieldname][0, 0]            # (96854,1), modified in place
            for hemi, sl in [('lh', slice(0, NHEMI)), ('rh', slice(NHEMI, 2 * NHEMI))]:
                rec = reconstruct(load_metric(f'{g}/targets.{hemi}.32k_spherereg.func.gii'), fit or 'fit1')
                arr[sl, 0] = rec[key]
    sio.savemat(os.path.join(OUT, outname), {var: v}, do_compression=True,
                long_field_names=True)
    print('wrote', outname, flush=True)
    del v
    gc.collect()

# verification: reload one file, check a modified field and an untouched metadata field
chk = sio.loadmat(os.path.join(OUT, 'cifti_polarAngle_all_spherereg.mat'))['cifti_polarAngle']
orig = sio.loadmat(os.path.join(CONV, 'cifti_polarAngle_all.mat'))['cifti_polarAngle']
s = subjects[0]
a = chk[f'x{s}_fit1_polarangle_msmall'][0, 0]
b = orig[f'x{s}_fit1_polarangle_msmall'][0, 0]
sub_same = np.array_equal(a[2*NHEMI:], b[2*NHEMI:], equal_nan=True)
cort_diff = not np.array_equal(a[:2*NHEMI], b[:2*NHEMI], equal_nan=True)
meta_same = np.array_equal(chk['pos'][0, 0], orig['pos'][0, 0])
names_same = chk.dtype.names == orig.dtype.names
print(f'verify: subcortical unchanged={sub_same} cortical changed={cort_diff} '
      f'metadata pos unchanged={meta_same} field names identical={names_same}')
assert sub_same and cort_diff and meta_same and names_same
print('DONE')

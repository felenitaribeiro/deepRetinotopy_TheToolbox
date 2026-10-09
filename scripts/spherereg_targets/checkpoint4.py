#!/usr/bin/env python
"""Checkpoint 4: validate the new *_spherereg.mat files against the originals.
4.1 coverage, 4.2 distributions, 4.3 value ranges + myelin, 4.4 split halves.
(4.5 loader test and 4.6 plots are separate scripts.)
Writes checks/checkpoint4.csv and prints a summary."""
import sys, os, csv
import numpy as np
import scipy.io as sio
from scipy.stats import ks_2samp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import WORK, CONV, NHEMI, roi_mask, circ_diff, circ_mean

LBL = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/labels/VisualAreasLabels_Wang2015'
NEW = f'{WORK}/mat'
subs = [s.strip() for s in open(f'{WORK}/subjects.txt') if s.strip()]

def area_mask(area, hemi):
    """V1/V2/V3 mask (dorsal+ventral+fovea) for one hemisphere at 32k."""
    sl = slice(0, NHEMI) if hemi == 'lh' else slice(NHEMI, 2 * NHEMI)
    m = np.zeros(NHEMI, bool)
    for part in [f'{area}d', f'{area}v']:
        v = sio.loadmat(f'{LBL}/{part}_labels.mat')[part][:, 0]
        m |= np.nan_to_num(v[sl]) > 0.5
    fv = sio.loadmat(f'{LBL}/fovea_{area}_labels.mat')[f'fovea_{area}'][:, 0]
    m |= np.nan_to_num(fv[sl]) > 0.5
    return m

print('loading mats ...', flush=True)
def load(name, var, newdir=False):
    d = NEW if newdir else CONV
    fn = name if not newdir else name.replace('_all.mat', '_all_spherereg.mat')
    return sio.loadmat(os.path.join(d, fn))[var]

pairs = {}
for m, var in [('polarAngle', 'cifti_polarAngle'), ('eccentricity', 'cifti_eccentricity'),
               ('pRFsize', 'cifti_pRFsize'), ('R2', 'cifti_R2'), ('myelin', 'cifti_myelin')]:
    pairs[m] = (load(f'cifti_{m}_all.mat', var), load(f'cifti_{m}_all.mat', var, True))
for m, var in [('polarAngle', 'cifti_polarAngle'), ('eccentricity', 'cifti_eccentricity'),
               ('pRFsize', 'cifti_pRFsize')]:
    for fit in ['fit2', 'fit3']:
        pairs[f'{m}_{fit}'] = (load(f'cifti_{m}_{fit}_all.mat', var),
                               load(f'cifti_{m}_{fit}_all.mat', var, True))

FIELD = {'polarAngle': 'polarangle', 'eccentricity': 'eccentricity', 'pRFsize': 'receptivefieldsize'}
def fld(struct, sub, m, fit='fit1'):
    if m == 'myelin':
        return struct[f'x{sub}_myelinmap'][0, 0][:, 0]
    if m == 'R2':
        return struct[f'x{sub}_fit1_r2_msmall'][0, 0][:, 0]
    return struct[f'x{sub}_{fit}_{FIELD[m]}_msmall'][0, 0][:, 0]

rows, fails = [], []
V = {h: {a: area_mask(a, h) for a in ['V1', 'V2', 'V3']} for h in ['lh', 'rh']}
for sub in subs:
    for hemi in ['lh', 'rh']:
        sl = slice(0, NHEMI) if hemi == 'lh' else slice(NHEMI, 2 * NHEMI)
        roi = roi_mask(hemi)
        row = {'sub': sub, 'hemi': hemi}
        paO = fld(pairs['polarAngle'][0], sub, 'polarAngle')[sl]
        paN = fld(pairs['polarAngle'][1], sub, 'polarAngle')[sl]
        ecO = fld(pairs['eccentricity'][0], sub, 'eccentricity')[sl]
        ecN = fld(pairs['eccentricity'][1], sub, 'eccentricity')[sl]
        szO = fld(pairs['pRFsize'][0], sub, 'pRFsize')[sl]
        szN = fld(pairs['pRFsize'][1], sub, 'pRFsize')[sl]
        r2O = fld(pairs['R2'][0], sub, 'R2')[sl]
        r2N = fld(pairs['R2'][1], sub, 'R2')[sl]
        myO = fld(pairs['myelin'][0], sub, 'myelin')[sl]
        myN = fld(pairs['myelin'][1], sub, 'myelin')[sl]
        # 4.1 coverage
        covO = np.mean(np.isfinite(paO[roi]) & np.isfinite(ecO[roi]))
        covN = np.mean(np.isfinite(paN[roi]) & np.isfinite(ecN[roi]))
        row['cov_before'], row['cov_after'] = float(covO), float(covN)
        if covO - covN > 0.05:
            fails.append((sub, hemi, f'coverage drop {covO-covN:.3f}'))
        # 4.2 distributions (frame-specific R2>15 masks)
        mO = roi & (r2O > 15) & np.isfinite(paO)
        mN = roi & (r2N > 15) & np.isfinite(paN)
        row['n_before'], row['n_after'] = int(mO.sum()), int(mN.sum())
        row['pa_cmean_before'] = circ_mean(paO[mO]); row['pa_cmean_after'] = circ_mean(paN[mN])
        row['pa_cmean_shift'] = float(np.abs((row['pa_cmean_after'] - row['pa_cmean_before'] + 180) % 360 - 180))
        for name, a, b in [('ecc', ecO, ecN), ('prf', szO, szN), ('r2', r2O, r2N)]:
            medO, medN = np.nanmedian(a[mO]), np.nanmedian(b[mN])
            row[f'{name}_med_before'], row[f'{name}_med_after'] = float(medO), float(medN)
            row[f'{name}_med_relchg'] = float(abs(medN - medO) / abs(medO)) if medO else np.nan
            row[f'{name}_ks'] = float(ks_2samp(a[mO][np.isfinite(a[mO])], b[mN][np.isfinite(b[mN])]).statistic)
            if row[f'{name}_med_relchg'] > 0.05:
                fails.append((sub, hemi, f'{name} median change {row[f"{name}_med_relchg"]:.3f}'))
        if row['pa_cmean_shift'] > 5:
            fails.append((sub, hemi, f'pa circ-mean shift {row["pa_cmean_shift"]:.1f}'))
        # 4.3 ranges
        ok = (np.nanmin(paN) >= 0 and np.nanmax(paN) <= 360 and np.nanmin(ecN) >= 0
              and np.nanmin(szN) >= 0 and np.nanmin(r2N) >= -1e-6 and np.nanmax(r2N) <= 100 + 1e-6)
        row['range_ok'] = bool(ok)
        row['all_nan'] = bool(np.all(~np.isfinite(paN)))
        if not ok: fails.append((sub, hemi, 'range violation'))
        if row['all_nan']: fails.append((sub, hemi, 'all-NaN participant'))
        # myelin
        row['my_min_before'], row['my_max_before'] = float(np.nanmin(myO)), float(np.nanmax(myO))
        row['my_min_after'], row['my_max_after'] = float(np.nanmin(myN)), float(np.nanmax(myN))
        v123 = V[hemi]['V1'] | V[hemi]['V2'] | V[hemi]['V3']
        mmO, mmN = np.nanmedian(myO[v123]), np.nanmedian(myN[v123])
        row['my_v123_med_relchg'] = float(abs(mmN - mmO) / abs(mmO))
        v1O = np.nanmedian(myO[V[hemi]['V1']]); v23O = np.nanmedian(myO[V[hemi]['V2'] | V[hemi]['V3']])
        v1N = np.nanmedian(myN[V[hemi]['V1']]); v23N = np.nanmedian(myN[V[hemi]['V2'] | V[hemi]['V3']])
        row['my_v1_gt_v23_before'] = bool(v1O > v23O); row['my_v1_gt_v23_after'] = bool(v1N > v23N)
        if row['my_v123_med_relchg'] > 0.05: fails.append((sub, hemi, 'myelin V1-3 median change >5%'))
        if row['my_v1_gt_v23_before'] and not row['my_v1_gt_v23_after']:
            fails.append((sub, hemi, 'myelin V1>V2/V3 pattern lost'))
        # 4.4 split halves
        pa2O = fld(pairs['polarAngle_fit2'][0], sub, 'polarAngle', 'fit2')[sl]
        pa3O = fld(pairs['polarAngle_fit3'][0], sub, 'polarAngle', 'fit3')[sl]
        pa2N = fld(pairs['polarAngle_fit2'][1], sub, 'polarAngle', 'fit2')[sl]
        pa3N = fld(pairs['polarAngle_fit3'][1], sub, 'polarAngle', 'fit3')[sl]
        mhO = mO & np.isfinite(pa2O) & np.isfinite(pa3O)
        mhN = mN & np.isfinite(pa2N) & np.isfinite(pa3N)
        row['split_before'] = float(np.median(circ_diff(pa2O[mhO], pa3O[mhO])))
        row['split_after'] = float(np.median(circ_diff(pa2N[mhN], pa3N[mhN])))
        if abs(row['split_after'] - row['split_before']) > 1:
            fails.append((sub, hemi, f'split-half change {row["split_after"]-row["split_before"]:.2f} deg'))
        rows.append(row)
    if subs.index(sub) % 30 == 29:
        print(f'{subs.index(sub)+1}/{len(subs)}', flush=True)

os.makedirs(f'{WORK}/checks', exist_ok=True)
cols = list(rows[0].keys())
with open(f'{WORK}/checks/checkpoint4.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

import statistics
print('\n=== checkpoint 4 summary (median [min,max] over subject-hemis) ===')
for key in ['cov_before', 'cov_after', 'pa_cmean_shift', 'ecc_med_relchg', 'prf_med_relchg',
            'r2_med_relchg', 'ecc_ks', 'prf_ks', 'r2_ks', 'my_v123_med_relchg',
            'split_before', 'split_after']:
    vals = [r[key] for r in rows if np.isfinite(r[key])]
    print(f'{key}: {statistics.median(vals):.4f} [{min(vals):.4f},{max(vals):.4f}]')
print(f'\nrange_ok all: {all(r["range_ok"] for r in rows)}; '
      f'all-NaN any: {any(r["all_nan"] for r in rows)}; '
      f'V1>V2/V3 after: {sum(r["my_v1_gt_v23_after"] for r in rows)}/{len(rows)}')
print(f'\nFAILURES ({len(fails)}):')
for f_ in fails[:60]:
    print('  ', *f_)
print('PASS' if not fails else 'SEE FAILURES')

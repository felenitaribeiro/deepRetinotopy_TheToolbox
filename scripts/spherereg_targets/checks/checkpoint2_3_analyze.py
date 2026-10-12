#!/usr/bin/env python
"""Full-cohort checkpoint metrics -> checks/full_metrics.csv (one row per subject/hemi).
Covers checkpoints 0.3, 1.2, 2.1-2.3, 3.1-3.2, myelin route agreement.
Run after resampling. Usage: analyze_full.py [subjects...]"""
import sys, os, csv, subprocess
import numpy as np
import nibabel as nib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import (WORK, NHEMI, load_metric, reconstruct, circ_diff, roi_mask,
                 orig_maps, med_p90)

FSBASE = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/freesurfer'
subs = sys.argv[1:] or [s.strip() for s in open(f'{WORK}/subjects.txt') if s.strip()]
mats = {}

WB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'wb')

def wb(*args):
    subprocess.run([WB] + list(args), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def native_roi(sub, hemi):
    g = f'{WORK}/gii/{sub}'
    roinat_f = f'{g}/roi.{hemi}.native.func.gii'
    if not os.path.exists(roinat_f):
        H = 'L' if hemi == 'lh' else 'R'
        tmp = f'{g}/roi.{hemi}.32k.func.gii'
        d = nib.gifti.GiftiDataArray(roi_mask(hemi).astype(np.float32),
                                     intent='NIFTI_INTENT_NONE', datatype='NIFTI_TYPE_FLOAT32')
        nib.save(nib.gifti.GiftiImage(darrays=[d]), tmp)
        wb('-set-structure', tmp, 'CORTEX_LEFT' if hemi == 'lh' else 'CORTEX_RIGHT')
        wb('-metric-resample', tmp, f'{WORK}/templates/S1200.{H}.sphere.32k_fs_LR.surf.gii',
           f'{WORK}/hcp/{sub}/{sub}.{H}.sphere.MSMAll.native.surf.gii', 'BARYCENTRIC', roinat_f)
    return nib.load(roinat_f).darrays[0].data > 0.5

rows = []
pa_change = {'lh': {}, 'rh': {}}   # per-hemi signed PA change fields for cp3.3
disp_field = {'lh': {}, 'rh': {}}
for si, sub in enumerate(subs):
    for hemi in ['lh', 'rh']:
        g = f'{WORK}/gii/{sub}'
        row = {'sub': sub, 'hemi': hemi}
        o = orig_maps(sub, hemi, mats=mats)
        roi = roi_mask(hemi)
        base = roi & (o['r2'] > 15) & np.isfinite(o['pa'])
        # cp0.3 hemifield fraction
        pa = o['pa'][base]
        right = (pa >= 270) | (pa <= 90)
        row['hemifield_frac'] = float(np.mean(right if hemi == 'lh' else ~right))
        # cp1.2 curvature recompute
        rec = nib.load(f'{g}/curv_recomputed.{hemi}.32k.func.gii').darrays[0].data
        trn = nib.load(f'{FSBASE}/{sub}/surf/{sub}.curvature-midthickness.{hemi}.32k_fs_LR.func.gii').darrays[0].data
        row['curv_corr'] = float(np.corrcoef(rec, trn)[0, 1])
        row['curv_maxabs'] = float(np.abs(rec - trn).max())
        # cp2.1 control round trip
        rt = reconstruct(load_metric(f'{g}/targets.{hemi}.32k_msmallRT.func.gii'))
        m = base & np.isfinite(rt['pa'])
        row['rt_msm_pa_med'], row['rt_msm_pa_p90'] = med_p90(circ_diff(rt['pa'][m], o['pa'][m]))
        row['rt_msm_ecc_med'] = float(np.nanmedian(np.abs(rt['ecc'][m] - o['ecc'][m])))
        # cp2.2 spherereg round trip
        sr = reconstruct(load_metric(f'{g}/targets.{hemi}.32k_spherereg.func.gii'))
        srt = reconstruct(load_metric(f'{g}/targets.{hemi}.32k_sphereregRT.func.gii'))
        m2 = roi & np.isfinite(sr['pa']) & np.isfinite(srt['pa']) & (sr['r2'] > 15)
        row['rt_sreg_pa_med'], row['rt_sreg_pa_p90'] = med_p90(circ_diff(srt['pa'][m2], sr['pa'][m2]))
        row['rt_sreg_ecc_med'] = float(np.nanmedian(np.abs(srt['ecc'][m2] - sr['ecc'][m2])))
        # cp2.3 native consistency
        nat = reconstruct(load_metric(f'{g}/targets.{hemi}.native.func.gii'))
        nsr = reconstruct(load_metric(f'{g}/targets.{hemi}.native_spherereg.func.gii'))
        rn = native_roi(sub, hemi)
        m3 = rn & np.isfinite(nat['pa']) & np.isfinite(nsr['pa']) & (nat['r2'] > 15)
        row['nat_pa_med'], row['nat_pa_p90'] = med_p90(circ_diff(nsr['pa'][m3], nat['pa'][m3]))
        # cp3.1 frame change
        m4 = base & np.isfinite(sr['pa'])
        row['frame_pa_med'], row['frame_pa_p90'] = med_p90(circ_diff(sr['pa'][m4], o['pa'][m4]))
        # signed change field for cp3.3 (NaN outside m4)
        chg = np.full(NHEMI, np.nan)
        chg[m4] = (sr['pa'][m4] - o['pa'][m4] + 180.0) % 360.0 - 180.0
        pa_change.setdefault(hemi, {})[sub] = chg[roi]
        # cp3.2 displacement
        a = np.stack([d.data for d in nib.load(f'{g}/xyz.{hemi}.32k_msmall.func.gii').darrays], 1)
        b = np.stack([d.data for d in nib.load(f'{g}/xyz.{hemi}.32k_spherereg.func.gii').darrays], 1)
        dist = np.linalg.norm(a - b, axis=1)
        row['disp_med'], row['disp_p90'] = med_p90(dist[roi])
        disp_field[hemi][sub] = dist[roi]
        # myelin route agreement (only when the mat-route file exists)
        f2 = f'{g}/myelin_mat.{hemi}.32k_spherereg.func.gii'
        if os.path.exists(f2):
            natmy = nib.load(f'{g}/myelin.{hemi}.32k_spherereg.func.gii').darrays[0].data.astype(float)
            roimy = nib.load(f'{g}/myelin_roi.{hemi}.32k_spherereg.func.gii').darrays[0].data.astype(float)
            mm = load_metric(f2)
            v = mm['validm']
            with np.errstate(invalid='ignore', divide='ignore'):
                a1 = np.where(roimy >= 0.99, natmy / np.where(roimy > 0, roimy, np.nan), np.nan)
                a2 = np.where(v >= 0.99, mm['myelin'] / np.where(v > 0, v, np.nan), np.nan)
            mg = np.isfinite(a1) & np.isfinite(a2)
            row['myelin_route_corr'] = float(np.corrcoef(a1[mg], a2[mg])[0, 1])
        rows.append(row)
    if (si + 1) % 20 == 0:
        print(f'{si+1}/{len(subs)}', flush=True)

os.makedirs(f'{WORK}/checks', exist_ok=True)
cols = sorted({k for r in rows for k in r}, key=lambda c: (c not in ('sub', 'hemi'), c))
# subset runs (explicit subject args) must never clobber the full-cohort CSV
csv_name = 'full_metrics.csv' if len(sys.argv) <= 1 else 'full_metrics_subset.csv'
with open(f'{WORK}/checks/{csv_name}', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

# cp3.3: consistency of the change across participants
print('\n=== cp3.3 cross-participant consistency ===')
summ = {}
for hemi in ['lh', 'rh']:
    for name, fields in [('pa_change', pa_change[hemi]), ('displacement', disp_field[hemi])]:
        M = np.stack([fields[s] for s in subs])
        mean_field = np.nanmean(M, axis=0)
        cors = []
        for i in range(len(subs)):
            x, y = M[i], mean_field
            ok = np.isfinite(x) & np.isfinite(y)
            if ok.sum() > 10:
                cors.append(np.corrcoef(x[ok], y[ok])[0, 1])
        summ[f'{hemi}_{name}'] = (float(np.median(cors)), float(np.min(cors)), float(np.max(cors)))
        print(f'{hemi} {name}: corr with group mean field median={np.median(cors):.3f} '
              f'range=[{np.min(cors):.3f},{np.max(cors):.3f}]')

# summary table
print('\n=== summary over subjects (median [min,max]) ===')
import statistics
def agg(key, hemi):
    vals = [r[key] for r in rows if r['hemi'] == hemi and key in r and np.isfinite(r[key])]
    return f'{statistics.median(vals):.3f} [{min(vals):.3f},{max(vals):.3f}]'
for key in ['hemifield_frac', 'curv_corr', 'curv_maxabs', 'rt_msm_pa_med', 'rt_msm_pa_p90',
            'rt_msm_ecc_med', 'rt_sreg_pa_med', 'rt_sreg_pa_p90', 'rt_sreg_ecc_med',
            'nat_pa_med', 'nat_pa_p90', 'frame_pa_med', 'frame_pa_p90', 'disp_med',
            'disp_p90', 'myelin_route_corr']:
    try:
        print(f'{key}: lh {agg(key,"lh")} | rh {agg(key,"rh")}')
    except Exception:
        pass
print(f'CSV written to checks/{csv_name}')

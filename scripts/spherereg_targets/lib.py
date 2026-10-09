"""Shared helpers: load metric GIFTIs, reconstruct maps (step 4), circular stats."""
import numpy as np
import nibabel as nib
import scipy.io as sio

WORK = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets'
CONV = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/raw/converted'
ROIMAT = '/scratch/project_mnt/S0210/deepRetinotopy_validation/functions/rois/EarlyVisualCortex/ROI_V1-3.mat'
NHEMI = 32492
PILOT = ['100610', '102311', '102816', '104416', '105923']
VALID_THR = 0.99


def load_metric(path):
    """Return dict name -> float64 array, using the Name metadata of each column."""
    img = nib.load(path)
    out = {}
    for i, d in enumerate(img.darrays):
        name = dict(d.meta).get('Name', f'col{i}')
        out[name] = np.asarray(d.data, dtype=np.float64)
    return out


def reconstruct(metric, fit='fit1'):
    """Step 4: rebuild polar angle / ecc / pRF / R2 from a resampled targets metric.
    Returns dict with pa, ecc, prf, r2 (r2 only for fit1), valid (the resampled
    validity column); maps are NaN where valid < VALID_THR."""
    v = metric[f'valid_{fit}']
    good = v >= VALID_THR
    with np.errstate(divide='ignore', invalid='ignore'):
        pa = np.degrees(np.arctan2(metric[f'sin_{fit}'], metric[f'cos_{fit}'])) % 360.0
        out = {'pa': np.where(good, pa, np.nan),
               'ecc': np.where(good, np.maximum(metric[f'ecc_{fit}'] / v, 0.0), np.nan),
               'prf': np.where(good, np.maximum(metric[f'prf_{fit}'] / v, 0.0), np.nan),
               'valid': v}
        if f'r2_{fit}' in metric:
            out['r2'] = np.where(good, np.maximum(metric[f'r2_{fit}'] / v, 0.0), np.nan)
    return out


def circ_diff(a, b):
    """Absolute circular difference in degrees."""
    return np.abs((a - b + 180.0) % 360.0 - 180.0)


def circ_mean(a):
    """Circular mean in degrees of angles in degrees."""
    r = np.deg2rad(a)
    return np.degrees(np.arctan2(np.nanmean(np.sin(r)), np.nanmean(np.cos(r)))) % 360.0


def roi_mask(hemi):
    roi = sio.loadmat(ROIMAT)['ROI'][:, 0]
    return (roi[:NHEMI] if hemi == 'lh' else roi[NHEMI:]) > 0.5


def orig_maps(sub, hemi, fit='fit1', mats=None):
    """Original maps for one subject/hemisphere straight from the .mat files.
    mats: optional dict to cache loaded structs across calls."""
    sl = slice(0, NHEMI) if hemi == 'lh' else slice(NHEMI, 2 * NHEMI)
    if mats is None:
        mats = {}
    def get(short, var):
        fname = f'cifti_{short}_all.mat' if fit == 'fit1' else f'cifti_{short}_{fit}_all.mat'
        if fname not in mats:
            mats[fname] = sio.loadmat(f'{CONV}/{fname}')[var]
        return mats[fname]
    field = {'polarAngle': 'polarangle', 'eccentricity': 'eccentricity',
             'pRFsize': 'receptivefieldsize'}
    out = {}
    for short, key in [('polarAngle', 'pa'), ('eccentricity', 'ecc'), ('pRFsize', 'prf')]:
        var = f'cifti_{short}'
        out[key] = get(short, var)[f'x{sub}_{fit}_{field[short]}_msmall'][0, 0][sl, 0]
    if fit == 'fit1':
        if 'cifti_R2_all.mat' not in mats:
            mats['cifti_R2_all.mat'] = sio.loadmat(f'{CONV}/cifti_R2_all.mat')['cifti_R2']
        out['r2'] = mats['cifti_R2_all.mat'][f'x{sub}_fit1_r2_msmall'][0, 0][sl, 0]
    return out


def med_p90(x):
    x = x[np.isfinite(x)]
    return (np.median(x), np.percentile(x, 90)) if x.size else (np.nan, np.nan)

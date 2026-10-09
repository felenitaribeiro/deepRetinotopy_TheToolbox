import csv, sys
import numpy as np
sys.path.insert(0, '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets/scripts')
from lib import WORK, NHEMI, load_metric, reconstruct, roi_mask, orig_maps
rows=list(csv.DictReader(open(f'{WORK}/checks/full_metrics.csv')))
f=lambda r,k: float(r[k])
ex_med=[(r['sub'],r['hemi'],f(r,'rt_msm_pa_med')) for r in rows if f(r,'rt_msm_pa_med')>=2.5]
ex_p90=[(r['sub'],r['hemi'],f(r,'rt_msm_pa_p90')) for r in rows if f(r,'rt_msm_pa_p90')>=7]
ex_ecc=[(r['sub'],r['hemi'],f(r,'rt_msm_ecc_med')) for r in rows if f(r,'rt_msm_ecc_med')>=0.15]
print('CP2.1 exceedances: pa_med>=2.5:',len(ex_med),' pa_p90>=7:',len(ex_p90),' ecc_med>=0.15:',len(ex_ecc))
print(' p90 worst:',sorted(ex_p90,key=lambda x:-x[2])[:5])
print(' ecc worst:',sorted(ex_ecc,key=lambda x:-x[2])[:5])
ex2=[r for r in rows if f(r,'rt_sreg_pa_med')>=2.5 or f(r,'rt_sreg_pa_p90')>=7 or f(r,'rt_sreg_ecc_med')>=0.15]
ex3=[r for r in rows if f(r,'nat_pa_med')>=2.5]
print('CP2.2 exceedances:',len(ex2),' CP2.3 exceedances:',len(ex3))
# CP3.3 sign-consistency of signed PA / ecc change at each ROI vertex
subs=[s.strip() for s in open(f'{WORK}/subjects.txt') if s.strip()]
mats={}
for hemi in ['lh','rh']:
    roi=roi_mask(hemi)
    nroi=roi.sum()
    pa_chg=np.full((len(subs),nroi),np.nan); ecc_chg=np.full((len(subs),nroi),np.nan)
    for i,sub in enumerate(subs):
        o=orig_maps(sub,hemi,mats=mats)
        new=reconstruct(load_metric(f'{WORK}/gii/{sub}/targets.{hemi}.32k_spherereg.func.gii'))
        m=(o['r2']>15)&np.isfinite(o['pa'])&np.isfinite(new['pa'])
        mr=m[roi]
        pa_chg[i,mr]=((new['pa']-o['pa']+180)%360-180)[roi][mr]
        ecc_chg[i,mr]=(new['ecc']-o['ecc'])[roi][mr]
    for name,M in [('pa',pa_chg),('ecc',ecc_chg)]:
        nval=np.isfinite(M).sum(0)
        keep=nval>=30
        mean_field=np.nanmean(M[:,keep],0)
        agree=np.nanmean(np.sign(M[:,keep])==np.sign(mean_field),0)
        print(f'{hemi} {name}-change sign agreement with group mean: median {np.nanmedian(agree):.3f} '
              f'p10 {np.nanpercentile(agree,10):.3f} (vertices kept: {keep.sum()}/{nroi}); '
              f'group-mean |change| median {np.nanmedian(np.abs(mean_field)):.3f}')

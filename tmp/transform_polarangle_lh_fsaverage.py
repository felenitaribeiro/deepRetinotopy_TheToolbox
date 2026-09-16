"""Post-hoc LH polar angle transform for benchmark (fsaverage-space) predictions.

Legacy single-map polarAngle models (like the myelincurv benchmark models) are
trained on LH targets shifted by +/-180 deg (read_HCP, utils/read_data.py), so
their LH predictions come out in that shifted frame. This script applies the
+/-180 involution to produce copies in the UNSHIFTED frame (right visual field:
270 -> 360/0 -> 90 deg), i.e. the frame of the visualCoord model's maps, the
raw .mat values, and Step-3 native-space outputs.

Frame bookkeeping (verified on subject 100610):
  - fs_empirical_polarAngle_lh*.func.gii on disk are SHIFTED -- the RAW
    myelincurv LH predictions compare against those directly, no transform.
  - visualCoord baseline LH maps are UNSHIFTED -- compare those against the
    _transformed outputs of this script (or unshift at analysis time like the
    sandbox dashboard builders' unshift() helper does).
Pick one frame per comparison; never mix.

Reads  <sub>/deepRetinotopy/<sub>.fs_predicted_polarAngle_lh_<feat>_<model>.func.gii
writes <sub>...<model>_transformed.func.gii alongside it. The raw file is never
touched and the output is always recomputed from it, so reruns are safe (the
shift is its own inverse -- an in-place version would undo itself if run twice).
Background vertices (-1) are preserved.
"""
import argparse
import os
import os.path as osp
import nibabel as nib


def main():
    parser = argparse.ArgumentParser(
        description='Unshift LH polar angle benchmark predictions (fsaverage space)')
    parser.add_argument('--path', type=str, required=True,
                        help='FreeSurfer-style subjects directory')
    parser.add_argument('--feat', type=str, default='myelincurvFeat',
                        help='Feature token in the prediction filename')
    parser.add_argument('--model', type=str, default='polarAngle-model',
                        help='Model token in the prediction filename')
    args = parser.parse_args()

    subjects = sorted(
        s for s in os.listdir(args.path)
        if osp.isdir(osp.join(args.path, s, 'deepRetinotopy'))
        and not s.startswith('processed_') and s != 'fsaverage')

    done, missing = 0, []
    for sub in subjects:
        raw_path = osp.join(
            args.path, sub, 'deepRetinotopy',
            f'{sub}.fs_predicted_polarAngle_lh_{args.feat}_{args.model}.func.gii')
        if not osp.exists(raw_path):
            missing.append(sub)
            continue
        img = nib.load(raw_path)
        pa = img.agg_data()
        mask = pa == -1
        add_180 = pa <= 180
        subtract_180 = pa > 180
        pa[add_180] += 180
        pa[subtract_180] -= 180
        pa[mask] = -1
        img.agg_data()[:] = pa
        out_path = raw_path.replace(f'{args.model}.func.gii',
                                    f'{args.model}_transformed.func.gii')
        nib.save(img, out_path)
        done += 1

    print(f'Transformed LH polarAngle maps for {done}/{len(subjects)} subjects '
          f'({args.feat}, {args.model}).')
    if missing:
        print(f'WARNING: no raw LH map for {len(missing)} subjects: {missing}')


if __name__ == '__main__':
    main()

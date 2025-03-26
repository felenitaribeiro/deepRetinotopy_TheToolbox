#!/usr/bin/env python
import argparse
import nibabel as nib

def transform(args):
    """
    Transform the polar angle map, such that the right visual field ranges from 270 (LVM) to 360/0 (HM) to 90 (UVM) degrees.
    Note: This transformation is required for the polar angle map from the left hemisphere.
    
    Parameters
    ----------
    polarAngle : numpy.ndarray
        The polar angle in degrees.
        
    Returns
    -------
    numpy.ndarray
        The transformed polar angle in degrees.
    """
    path_dirs = args.path.split('/')
    index_sub = path_dirs.index('deepRetinotopy') - 1
    subject = path_dirs[index_sub]

    data = nib.load(args.path + subject + 
                            '.predicted_polarAngle_' +  args.model + '.lh.native.func.gii')
    polarAngle = data.agg_data()
    mask = polarAngle == -1
    
    # Transform the polar angle map from the left hemisphere to cover the right visual field,
    # i.e., from 270 (LVM) to 360/0 (HM) to 90 (UVM) degrees.
    add_180 = polarAngle <= 180
    subtract_180 = polarAngle > 180
    polarAngle[add_180] += 180
    polarAngle[subtract_180] -= 180

    # Mask out vertices without predictions
    polarAngle[mask] = -1
    data.agg_data()[:] = polarAngle
    nib.save(data, args.path + subject + 
                            '.predicted_polarAngle_' +  args.model + '.lh.native.func.gii')
    return polarAngle
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transform the polar angle map for the left hemisphere')
    parser.add_argument('--path', type=str, help='Path to the polar angle maps')
    parser.add_argument('--model', type=str, help='Model number')
    args = parser.parse_args()
    transform(args)
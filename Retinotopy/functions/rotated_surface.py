import numpy as np
import os.path as osp


rotated_info = open(osp.join(osp.dirname(osp.realpath(__file__)),
                             '../labels/rotated_surf/SurfToSurf.1D'))
lines = rotated_info.readlines()

def rotate_roi(index_L_mask):
    """New mask for the selection of an ROI placed elsewhere in the cortical
    surface.

    Args:
        index_L_mask (list): Indices of the non-zero elements from
            final_mask_L (number of nonzero elements,)

    Returns:
        mask (numpy array): Mask of the new ROI from the left
            hemisphere (32492,)

        new_L_mask_indexes (list): Indices of the non-zero elements from
            final_mask_L (number of nonzero elements,)
    """

    new_index = []
    old_index = []
    for i in range(14,len(lines)):
        old_index.append(int(lines[i][:6].strip()))
        new_index.append(int(lines[i][6:-4].strip()))

    new_L_mask_indexes = []
    for j in range(len(index_L_mask)):
        new_L_mask_indexes.append(new_index[index_L_mask[j]])

    mask = np.zeros(32492,)
    mask[new_L_mask_indexes] = 1
    return mask, new_L_mask_indexes

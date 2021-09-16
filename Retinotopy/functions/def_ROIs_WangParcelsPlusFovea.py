import numpy as np
import os.path as osp
import scipy.io


def roi(list_of_labels):
    """Mask for the selection of the region of interest in the surface
    template.

    Args:
        list_of_labels (list): list with the file name (.mat) containing the
            region of interest (from both L and R hemispheres)

    Returns:
        final_mask_L (numpy array): Mask of the region of interest from left
            hemisphere (32492,)

        final_mask_R (numpy array): Mask of the region of interest from
            right hemisphere (32492,)

        index_L_mask (list): Indices of the non-zero elements from
            final_mask_L (number of nonzero elements,)

        index_R_mask (list): Indices of the non-zero elements from
            final_mask_R (number of nonzero elements,)

    """

    # Defining number of nodes
    number_cortical_nodes = int(64984)
    number_hemi_nodes = int(number_cortical_nodes / 2)

    list_primary_visual_areas = np.zeros([len(list_of_labels), 64984])
    for i in range(len(list_of_labels)):
        list_primary_visual_areas[i] = np.reshape(scipy.io.loadmat(
            osp.join(osp.dirname(osp.realpath(__file__)), '..',
                     'labels/ROI_WangPlusFovea',
                     list_of_labels[i] + '.mat'))[list_of_labels[i]][0:64984],
                                                  (-1))

    final_mask_L = np.sum(list_primary_visual_areas, axis=0)[
                   0:number_hemi_nodes]
    final_mask_R = np.sum(list_primary_visual_areas, axis=0)[
                   number_hemi_nodes:number_cortical_nodes]

    index_L_mask = [i for i, j in enumerate(final_mask_L) if j == 1]
    index_R_mask = [i for i, j in enumerate(final_mask_R) if j == 1]

    return final_mask_L, final_mask_R, index_L_mask, index_R_mask

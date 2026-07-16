import numpy as np
import os.path as osp
import scipy.io
import nibabel as nib

def ROIs_DorsalEarlyVisualCortex(list_of_labels):
    """Mask for the selection of the region of interest in the surface
    template.

    Args:
        list_of_labels (list): list with file names of visual areas masks (
            .mat), from both L and R hemispheres to be merged together.

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
                     'labels/ROI_DorsalEarlyVisualCortex',
                     list_of_labels[i] + '.mat'))[list_of_labels[i]][
            0:64984], (-1))
    # Merge all visual areas
    final_mask_L = np.sum(list_primary_visual_areas, axis=0)[
        0:number_hemi_nodes]
    final_mask_R = np.sum(list_primary_visual_areas, axis=0)[
        number_hemi_nodes:number_cortical_nodes]

    index_L_mask = [i for i, j in enumerate(final_mask_L) if j >= 1]
    index_R_mask = [i for i, j in enumerate(final_mask_R) if j >= 1]

    return final_mask_L, final_mask_R, index_L_mask, index_R_mask


def ROIs_WangParcels(list_of_labels):
    """Mask for the selection of the region of interest in the surface
    template.

    Args:
        list_of_labels (list): list with file names of visual areas masks (
            .mat), from both L and R hemispheres to be merged together.

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
                     'labels/VisualAreasLabels_Wang2015',
                     list_of_labels[i] + '_labels.mat'))[list_of_labels[i]][
            0:64984], (-1))
        # print(len(list_primary_visual_areas[i][list_primary_visual_areas[i] == 1]))

    # Merge all visual areas
    final_mask_L = np.sum(list_primary_visual_areas, axis=0)[
        0:number_hemi_nodes]
    final_mask_R = np.sum(list_primary_visual_areas, axis=0)[
        number_hemi_nodes:number_cortical_nodes]

    final_mask_L[np.isnan(final_mask_L)] = 0
    final_mask_R[np.isnan(final_mask_R)] = 0

    index_L_mask = [i for i, j in enumerate(final_mask_L) if j >= 1]
    index_R_mask = [i for i, j in enumerate(final_mask_R) if j >= 1]

    return final_mask_L, final_mask_R, index_L_mask, index_R_mask


def ROI_WangParcelsPlusFovea(list_of_labels):
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


def ROI_from_gifti(lh_label, rh_label):
    """Region-of-interest masks from a pair of per-hemisphere 32k_fs_LR label
    GIFTIs. Any nonzero label value counts as in-ROI. Same 4-tuple contract as
    ROI_WangParcelsPlusFovea, so it is a drop-in for the dataset / inference
    mask. Paths are resolved relative to the repo root unless absolute.

    Args:
        lh_label (str): path to the left-hemisphere .label.gii (32492,)
        rh_label (str): path to the right-hemisphere .label.gii (32492,)

    Returns:
        final_mask_L, final_mask_R (numpy arrays, 32492): 0/1 ROI masks.
        index_L_mask, index_R_mask (lists): indices of the in-ROI vertices.
    """
    number_hemi_nodes = int(32492)
    base = osp.join(osp.dirname(osp.realpath(__file__)), '..')

    def _load(p):
        p = p if osp.isabs(p) else osp.join(base, p)
        return np.asarray(nib.load(p).agg_data()).reshape(-1)[:number_hemi_nodes]

    final_mask_L = (_load(lh_label) != 0).astype(float)
    final_mask_R = (_load(rh_label) != 0).astype(float)
    index_L_mask = [i for i, j in enumerate(final_mask_L) if j == 1]
    index_R_mask = [i for i, j in enumerate(final_mask_R) if j == 1]
    return final_mask_L, final_mask_R, index_L_mask, index_R_mask


def ROI_wholebrain():
    """Whole-hemisphere ROI: every 32k_fs_LR vertex is in-ROI. The medial wall
    and low-signal vertices are NOT removed here -- they carry NaN pRF values
    (mapped to the -1 sentinel) and R2 ~ 0, so both the `R2 > 0` mask and the
    R2-weighted loss down-weight them to ~0 automatically. This is the
    'whole brain' condition (Experiment A)."""
    number_hemi_nodes = int(32492)
    final_mask_L = np.ones(number_hemi_nodes)
    final_mask_R = np.ones(number_hemi_nodes)
    index_mask = list(range(number_hemi_nodes))
    return final_mask_L, final_mask_R, list(index_mask), list(index_mask)


# ROI registry: maps an `--roi` name to a zero-arg callable returning the
# (final_mask_L, final_mask_R, index_L_mask, index_R_mask) 4-tuple.
# 'wholebrain' is the toolbox default (all 32492 vertices/hemisphere); it matches
# visual-cortex accuracy while keeping the model ready for later fine-tuning on
# high-eccentricity data. 'wang_fovea' (Wang V1-V3 + fovea) is kept for
# visual-cortex-only training / backward compatibility. Custom ROIs can be added
# with ROI_from_gifti(lh_label, rh_label).
ROI_REGISTRY = {
    'wholebrain': ROI_wholebrain,
    'wang_fovea': lambda: ROI_WangParcelsPlusFovea(['ROI']),
}


def get_roi(name):
    """Return (final_mask_L, final_mask_R, index_L_mask, index_R_mask) for a
    registered ROI name (see ROI_REGISTRY)."""
    if name not in ROI_REGISTRY:
        raise ValueError("Unknown ROI '{}'. Available: {}".format(
            name, ', '.join(sorted(ROI_REGISTRY))))
    return ROI_REGISTRY[name]()


if __name__ == '__main__':
    # Testing
    print("Testing the ROI selection")
    print("Dorsal ROI")
    mask_LH, mask_RH, _, _ = ROIs_DorsalEarlyVisualCortex(['ROI'])
    print("Number of nodes in the left and right hemispheres: %s, %s" %
          (np.sum(mask_LH), np.sum(mask_RH)))

    print("Wang parcels")
    mask_LH, mask_RH, _, _ = ROIs_WangParcels(
        ['V1v', 'V1d', 'V2v', 'V2d', 'V3v', 'V3d'])
    print("Number of nodes in the left and right hemispheres: %s, %s" %
          (np.sum(mask_LH), np.sum(mask_RH)))

    print("Wang parcels (V1-3) with fovea")
    mask_LH, mask_RH, _, _ = ROI_WangParcelsPlusFovea(['ROI'])
    print("Number of nodes in the left and right hemispheres: %s, %s" %
          (np.sum(mask_LH), np.sum(mask_RH)))

    for roi_name in ('wholebrain', 'wang_fovea'):
        mask_LH, mask_RH, _, _ = get_roi(roi_name)
        print("Registry '%s': L=%s, R=%s nodes" %
              (roi_name, int(np.sum(mask_LH)), int(np.sum(mask_RH))))

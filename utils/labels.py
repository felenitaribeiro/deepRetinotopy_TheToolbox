import numpy as np
import os.path as osp
import sys
import scipy.io
import torch_geometric.transforms as T
import torch
sys.path.append(osp.dirname(osp.realpath(__file__)))
from utils.rois import ROI_WangParcelsPlusFovea
from torch_geometric.data import Data

def labels(input, labels):
    """Function for the selection of triangular faces from the region of
    interest.

    Args:
        input (.mat file): .mat file with the triangular faces composing the
            surface template
        labels (numpy array): vertices' indeces from the region of interest

    Returns:
        numpy array: triangular faces from the region of interest (number of
            faces, 3)
    """

    # Vectorized equivalent of the original O(vertices x faces) loop: keep only
    # faces whose three vertices are ALL inside the ROI, and remap their global
    # vertex ids to ROI-local ids 0..len(labels)-1 (local id = position of the
    # vertex in `labels`, which is the ascending in-ROI order used for pos/x/y).
    #
    # The original built each interior face 3x (once per in-ROI vertex); those
    # duplicates are removed by T.FaceToEdge + to_undirected downstream, so the
    # resulting graph (edge_index) is identical. Verified edge-set-equal for the
    # visual-cortex ROIs (e.g. wang_fovea). This makes the whole-brain ROI (32492
    # vertices) build instantly instead of taking several minutes per hemisphere.
    input = np.asarray(input)
    labels = np.asarray(labels)
    number_hemi_nodes = int(32492)
    local = np.full(number_hemi_nodes, -1, dtype=np.int64)
    local[labels] = np.arange(len(labels))

    remapped = local[input]                     # (num_faces, 3), -1 outside ROI
    interior = (remapped >= 0).all(axis=1)       # faces fully inside the ROI
    return remapped[interior].astype(np.int64)


if __name__ == '__main__':
    list_of_labels = ['ROI']
    final_mask_L, final_mask_R, index_L_mask, index_R_mask = ROI_WangParcelsPlusFovea(
        list_of_labels)

    faces_R = labels(scipy.io.loadmat(osp.join(osp.dirname(osp.realpath(__file__)), '../utils/templates/tri_faces_R.mat'))[
        'tri_faces_R'] - 1, index_R_mask)
    faces_L = labels(scipy.io.loadmat(osp.join(osp.dirname(osp.realpath(__file__)), '../utils/templates/tri_faces_L.mat'))[
        'tri_faces_L'] - 1, index_L_mask)
    for faces in [faces_L, faces_R]:
        data = Data(face=torch.tensor(faces.T, dtype=torch.long))
        transform = T.FaceToEdge()
        data = transform(data)
        # 12 is the maximum number of edges per node as it is an undirected graph
        assert np.unique(data.edge_index, return_counts=True)[1].max() <= 12

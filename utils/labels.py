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

    # Append to faces_indexes the location of faces containing nodes from the
    # visual cortex
    faces_indexes = np.array([])
    for j in range(len(labels)):
        faces_indexes = np.concatenate(
            (faces_indexes, np.where(input == labels[j])[0]), axis=0)

    # Select indexed faces (faces_indexes)
    faces = []
    for i in range(len(faces_indexes)):
        faces.append(input[int(faces_indexes[i])])

    # Change the nodes' indeces from the visual system to range
    # from 0:len(labels)
    faces = np.array(faces) * 10000
    index = np.array(labels) * 10000
    for i in range(len(labels)):
        faces[np.where(faces == index[i])] = i

    # Select only faces composed of vertices that are within the ROI
    final_faces = []
    for i in range(len(faces)):
        if np.sum(faces <= len(labels) - 1, axis=1)[i] == 3:
            final_faces.append(faces[i])

    return np.reshape(final_faces, (len(final_faces), 3))


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

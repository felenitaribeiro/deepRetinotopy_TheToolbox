import numpy as np
import sys
import torch
import torch_geometric.transforms as T
import torch_geometric.data as Data
import random
sys.path.append('.')
from utils.metrics import *
from utils.labels import *
from utils.rois import *

# ROIs
def test_ROIs_DorsalEarlyVisualCortex():
    list_of_labels = ['ROI']
    final_mask_L, final_mask_R, index_L_mask, index_R_mask = ROIs_DorsalEarlyVisualCortex(
        list_of_labels)
    assert isinstance(final_mask_L, np.ndarray)
    assert isinstance(final_mask_R, np.ndarray)
    assert isinstance(index_L_mask, list)
    assert isinstance(index_R_mask, list)
    assert final_mask_L.shape == (32492,)
    assert final_mask_R.shape == (32492,)
    assert len(index_L_mask) > 0
    assert len(index_R_mask) > 0


def test_ROI_WangParcelsPlusFovea():
    list_of_labels = ['ROI']
    final_mask_L, final_mask_R, index_L_mask, index_R_mask = ROI_WangParcelsPlusFovea(
        list_of_labels)
    assert isinstance(final_mask_L, np.ndarray)
    assert isinstance(final_mask_R, np.ndarray)
    assert isinstance(index_L_mask, list)
    assert isinstance(index_R_mask, list)
    assert final_mask_L.shape == (32492,)
    assert final_mask_R.shape == (32492,)
    assert len(index_L_mask) > 0
    assert len(index_R_mask) > 0


def test_ROIs_WangParcels():
    list_of_labels = ['V1d', 'V2d', 'V3d']
    final_mask_L, final_mask_R, index_L_mask, index_R_mask = ROIs_WangParcels(
        list_of_labels)
    assert isinstance(final_mask_L, np.ndarray)
    assert isinstance(final_mask_R, np.ndarray)
    assert isinstance(index_L_mask, list)
    assert isinstance(index_R_mask, list)
    assert final_mask_L.shape == (32492,)
    assert final_mask_R.shape == (32492,)
    assert len(index_L_mask) > 0
    assert len(index_R_mask) > 0

# Labels
def test_labels():
    list_of_labels = ['ROI']
    final_mask_L, final_mask_R, index_L_mask, index_R_mask = ROI_WangParcelsPlusFovea(
        list_of_labels)

    faces_R = labels(scipy.io.loadmat(osp.join(osp.dirname(osp.realpath(__file__)), '../utils/templates/tri_faces_R.mat'))[
        'tri_faces_R'] - 1, index_R_mask)
    faces_L = labels(scipy.io.loadmat(osp.join(osp.dirname(osp.realpath(__file__)), '../utils/templates/tri_faces_L.mat'))[
        'tri_faces_L'] - 1, index_L_mask)
    assert isinstance(faces_R, np.ndarray)
    assert isinstance(faces_L, np.ndarray)
    assert faces_R.shape[-1] == 3
    assert faces_L.shape[-1] == 3

    for faces in [faces_L, faces_R]:
        data = Data(face=torch.tensor(faces.T, dtype=torch.long))
        transform = T.FaceToEdge()
        data = transform(data)
        assert np.unique(data.edge_index, return_counts=True)[1].max() <= 12

# Metrics
def test_smallest_angle():
    x = np.random.rand(100, 1)
    y = np.random.rand(100, 1)
    assert isinstance(smallest_angle(x, y), np.ndarray)
    assert smallest_angle(x, y).shape == (100, 1)
    assert smallest_angle(x, y).max() <= 360
    assert smallest_angle(x, y).min() >= 0


def test_distance_PolarCoord():
    radius1 = np.random.rand(100, 1)
    radius2 = np.random.rand(100, 1)
    theta1 = np.reshape(
        np.array([random.uniform(-np.pi, np.pi) for _ in range(100)]), (100, 1))
    theta2 = np.reshape(
        np.array([random.uniform(-np.pi, np.pi) for _ in range(100)]), (100, 1))
    assert isinstance(distance_PolarCoord(
        radius1, radius2, theta1, theta2), np.ndarray)
    assert distance_PolarCoord(
        radius1, radius2, theta1, theta2).shape == (100, 1)


def test_average_prediction():
    predictions_array = np.reshape(
        np.array([random.uniform(0, 360) for _ in range(30000)]), (100, 3, 100))
    assert isinstance(average_prediction(predictions_array), np.ndarray)
    assert average_prediction(predictions_array).shape == (100, 100)
    assert average_prediction(predictions_array).max() <= 360
    assert average_prediction(predictions_array).min() >= 0

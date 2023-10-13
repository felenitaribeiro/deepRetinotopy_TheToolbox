#%%
import os
import os.path as osp
import torch
import torch_geometric.transforms as T
import sys
import nibabel as nib
import numpy as np
import argparse

sys.path.append('..')

from utils.rois import ROI_WangParcelsPlusFovea as roi
from utils.rois import ROIs_WangParcels as parcels
from utils.model import deepRetinotopy
from torch_geometric.data import DataLoader
from utils.dataset import Retinotopy
from utils.metrics import average_prediction
#%%
path = '/home/uqfribe1/Desktop/deepRetinotopy_general/freesurfer/'
list_subs = os.listdir(path)
norm_value = 70.4237  # normalization parameter for distance between nodes
pre_transform = T.Compose([T.FaceToEdge()])
# Load the dataset
data = Retinotopy(path, 'Test',
                            transform=T.Cartesian(max_value=norm_value),
                            pre_transform=pre_transform, dataset='other',
                            list_subs=list_subs,
                            prediction='polarAngle', hemisphere='lh')
#%%
edge_index = data[0].edge_index
positions = data[0].pos

#%%
label_primary_visual_areas = ['ROI']
final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(
    label_primary_visual_areas)

#%%
polarAngle = nib.load(path + '/101/deepRetinotopy/101.fs_predicted_polarAngle_lh_curvatureFeat_average.func.gii').agg_data()[final_mask_L == 1]
sum = polarAngle <= 180
minus = polarAngle > 180
polarAngle[sum] = polarAngle[sum] + 180
polarAngle[minus] = polarAngle[minus] - 180

eccentricity = nib.load(path + '/101/deepRetinotopy/101.fs_predicted_eccentricity_lh_curvatureFeat_average.func.gii').agg_data()[final_mask_L == 1]
# %%
edge_index = edge_index.T
#%%
cross_product = []
for edge in edge_index:
    print(edge)
    print(polarAngle[edge[0]])
    print(eccentricity[edge[1]])
    x1 = eccentricity[edge[0]] * np.cos(polarAngle[edge[0]]/180*np.pi)
    y1 = eccentricity[edge[0]] * np.sin(polarAngle[edge[0]]/180*np.pi)
    x2 = eccentricity[edge[1]] * np.cos(polarAngle[edge[1]]/180*np.pi)
    y2 = eccentricity[edge[1]] * np.sin(polarAngle[edge[1]]/180*np.pi)
    cross_product.append(x1*y2 - x2*y1)
    print('------------------')
cross_product = np.array(cross_product)
# %%
sign = np.zeros(polarAngle.shape)
amplitude = np.zeros(polarAngle.shape)
for i in range(len(polarAngle)):
    edges_indeces = np.array(np.where(edge_index == i))
    cross_product_node = cross_product[edges_indeces[0][edges_indeces[1]==0]]
    amplitude[i] = np.sum(cross_product_node)
    # signs = np.sign(cross_product_node)
    # if np.sum(signs) == 0:
    #     sign[i] = np.sign(np.sum(cross_product_node))
    # else:
    #     sign[i] = np.sign(np.sum(signs))
    sign[i] = np.sign(np.sum(cross_product_node))

# %%
template = nib.load(path + '/101/deepRetinotopy/101.fs_predicted_polarAngle_lh_curvatureFeat_average.func.gii')
final_sign_map = np.zeros((32492, 1))
final_sign_map[final_mask_L == 1] = np.reshape(sign, (-1, 1))
final_sign_map[final_mask_L == 0] = -10
template.agg_data()[:] = np.reshape(final_sign_map, (-1))

nib.save(template, './signmap.func.gii')

# %%
# polarAngle = nib.load('tmp/101.predicted_polarAngle_average.lh.native.func.gii').agg_data()[final_mask_L == 1]
# eccentricity = nib.load('tmp/101.predicted_eccentricity_average.lh.native.func.gii').agg_data()[final_mask_L == 1]
# final_mask_L = nib.load('tmp/mask.func.gii').agg_data()[final_mask_L == 1]
# template = nib.load('tmp/101.predicted_polarAngle_average.lh.native.func.gii')

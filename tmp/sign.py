#%%
import os
import os.path as osp
import torch_geometric.transforms as T
import sys
import nibabel as nib
import numpy as np
import argparse
import sys
sys.path.append('./../')

from utils.rois import ROI_WangParcelsPlusFovea as roi
from utils.rois import ROIs_DorsalEarlyVisualCortex as ROI
from utils.rois import ROIs_WangParcels as parcels
from utils.dataset import Retinotopy
#%%
path = '/home/uqfribe1/Desktop/freesurfer'
list_subs = os.listdir(path)
norm_value = 70.4237 
pre_transform = T.Compose([T.FaceToEdge(remove_faces=False)])
data = Retinotopy(path, 'Test',
                            transform=T.Cartesian(max_value=norm_value),
                            pre_transform=pre_transform, dataset='other',
                            list_subs=list_subs,
                            prediction='polarAngle', hemisphere='lh')
#%%

def field_sign(path, edges, faces, hemisphere, polarAngle_file, eccentricity_file, mask_L, mask_R):
    """
    This function computes the visual field sign for each node in the cortical surface.
    
    Args:
        path (str): Path to the folder where the predicted polar angle and eccentricity maps are saved.
        edges (numpy.ndarray): The edges of the cortical surface.
        faces (numpy.ndarray): The faces of the cortical surface.
        polarAngle (str): file name of the predicted polar angle map.
        eccentricity (numpy.ndarray): file name of the predicted eccentricity map.
        region_of_interest (numpy.ndarray): The region of interest (ROI) of the cortical surface.
    Returns:
        None
    """
    # for hemisphere in ['lh', 'rh']:
    if hemisphere == 'lh':
        final_mask = mask_L
    else:
        final_mask = mask_R
    print(path + polarAngle_file)
    polarAngle = nib.load(path + polarAngle_file).agg_data()[final_mask == 1]
    eccentricity = nib.load(path + eccentricity_file).agg_data()[final_mask == 1]

    cross_product_faces = []
    for face in faces:
        x1 = eccentricity[face[0]] * np.cos(polarAngle[face[0]]/180*np.pi)
        y1 = eccentricity[face[0]] * np.sin(polarAngle[face[0]]/180*np.pi)
        x2 = eccentricity[face[1]] * np.cos(polarAngle[face[1]]/180*np.pi)
        y2 = eccentricity[face[1]] * np.sin(polarAngle[face[1]]/180*np.pi)
        x3 = eccentricity[face[2]] * np.cos(polarAngle[face[2]]/180*np.pi)
        y3 = eccentricity[face[2]] * np.sin(polarAngle[face[2]]/180*np.pi)
        cross_product_faces.append((x1*y2 - x2*y1) + (x2*y3 - x3*y2) + (x3*y1 - x1*y3))
    cross_product_faces = np.array(cross_product_faces)

    sign = np.zeros(polarAngle.shape)
    for i in range(len(polarAngle)):
        faces_indeces = np.array(np.where(faces == i))
        cross_product_node = cross_product_faces[faces_indeces[0]]
        signs = np.sign(cross_product_node)
        if np.sum(signs) == 0:
            sign[i] = np.sign(np.sum(cross_product_node))
        else:
            sign[i] = np.sign(np.sum(signs))

    template = nib.load(path + polarAngle_file)
    final_sign_map = np.zeros((32492, 1))
    final_sign_map[final_mask_L == 1] = np.reshape(sign, (-1, 1))
    final_sign_map[final_mask_L == 0] = -10
    template.agg_data()[:] = np.reshape(final_sign_map, (-1))

    nib.save(template, './' + polarAngle_file[0:7] + 'signmap_' + hemisphere + '.func.gii')
    return 

# Load edges and faces
edge_index = data[0].edge_index
faces = data[0].face

edges = edge_index.T
faces = faces.T

# Mask
label_primary_visual_areas = ['ROI']
final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(
    label_primary_visual_areas)
path = '/home/uqfribe1/Desktop/freesurfer/101_surf'

field_sign(path, edges, faces, 'lh',
           '101_surf.fs_predicted_polarAngle_lh_curvatureFeat_average.func.gii', 
           '101_surf.fs_predicted_eccentricity_lh_curvatureFeat_average.func.gii',
            final_mask_L, final_mask_R)

# %%
subs = ['114823', '157336', '581450']

for sub in subs:
    
    path = '/home/uqfribe1/PycharmProjects/deepRetinotopy_TheToolbox/grant/' + sub + '/deepRetinotopy/'
    field_sign(path, edges, faces, 'lh',
            sub + '.fs_predicted_polarAngle_lh_curvatureFeat_average.func.gii', 
            sub + '.fs_predicted_eccentricity_lh_curvatureFeat_average.func.gii',
            final_mask_L, final_mask_R)
# %%

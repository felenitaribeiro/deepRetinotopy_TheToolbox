#%%
import os
import os.path as osp
import torch_geometric.transforms as T
import sys
import nibabel as nib
import numpy as np
import argparse
import sys
import torch
import scipy
sys.path.append('./../')

from utils.rois import ROI_WangParcelsPlusFovea as roi
from utils.labels import labels
def field_sign(path, hemisphere, polarAngle_file, eccentricity_file):
    """
    This function computes the visual field sign for each node in the cortical surface.
    
    Args:
        path (str): Path to the folder where the predicted polar angle and eccentricity maps are saved.
        hemisphere (str): Hemisphere of the cortical surface. It can be 'lh' or 'rh'.
        polarAngle (str): file name of the predicted polar angle map.
        eccentricity (numpy.ndarray): file name of the predicted eccentricity map.
    Returns:
        print: The visual field sign map is saved in the same folder as the predicted polar angle and eccentricity maps.
    """
    
    # Mask
    label_primary_visual_areas = ['ROI']
    mask_L, mask_R, index_L_mask, index_R_mask = roi(
        label_primary_visual_areas)
    
    if hemisphere == 'lh':
        final_mask = mask_L
        faces_L = labels(scipy.io.loadmat(osp.join(osp.dirname(osp.realpath(__file__)), '../utils/templates/tri_faces_L.mat'))[
            'tri_faces_L'] - 1, index_L_mask)
        faces = torch.tensor(faces_L, dtype=torch.long)
    else:
        final_mask = mask_R
        faces_R = labels(scipy.io.loadmat(osp.join(osp.dirname(osp.realpath(__file__)), '../utils/templates/tri_faces_R.mat'))[
            'tri_faces_R'] - 1, index_R_mask)
        faces = torch.tensor(faces_R, dtype=torch.long)
    
    
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
    final_sign_map[final_mask == 1] = np.reshape(sign, (-1, 1))
    final_sign_map[final_mask == 0] = -10
    template.agg_data()[:] = np.reshape(final_sign_map, (-1))
    name = polarAngle_file.split('.')[0]
    save_path = path + name + '.fieldSignMap_' + hemisphere + '.func.gii'
    nib.save(template, save_path)
    return print('Visual field sign map has been saved as ' + save_path)


if __name__ == '__main__':

    args = argparse.ArgumentParser()
    args.add_argument('--path', type=str)
    args.add_argument('--hemisphere', type=str)
    args.add_argument('--polarAngle_file', type=str)
    args.add_argument('--eccentricity_file', type=str)
    args = args.parse_args()

    field_sign(args.path, args.hemisphere, args.polarAngle_file, args.eccentricity_file)

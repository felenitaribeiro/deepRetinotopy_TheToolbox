import numpy as np
import scipy.io
import os.path as osp
import torch

from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi
from Retinotopy.functions.plusFovea import add_fovea
from nilearn import plotting

subject_index = 7  # 7

hcp_id = ['617748', '191336', '572045', '725751', '198653',
          '601127', '644246', '191841', '680957', '157336']

path = './../../../Retinotopy/data/raw/converted'
curv = scipy.io.loadmat(osp.join(path, 'cifti_curv_all.mat'))['cifti_curv']
background = np.reshape(
    curv['x' + hcp_id[subject_index] + '_curvature'][0][0][0:32492], (-1))

threshold = 1  # threshold for the curvature map

# Background settings
nocurv = np.isnan(background)
background[nocurv == 1] = 0
background[background < 0] = 0
background[background > 0] = 1

early_visual_cortex = ['V1d', 'V1v', 'fovea_V1', 'V2d', 'V2v',
                       'fovea_V2', 'V3d', 'V3v', 'fovea_V3']
V1, V2, V3 = add_fovea(early_visual_cortex)
cluster = np.sum(
    [np.reshape(V1, (-1, 1)), np.reshape(V2, (-1, 1)),
     np.reshape(V3, (-1, 1))], axis=0)
cluster[V3 == 3] = 3
cluster[V2 == 2] = 2
cluster[V1 == 1] = 1

label = ['Early visual cortex']

# ROI
visual_hierarchy = ['ROI']
final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(
    visual_hierarchy)

# Selecting nodes
nodes = cluster[final_mask_L == 1]
nodes = np.where(nodes != 0)[0]

error_map = np.zeros((32492, 1))

# Loading error
induced_error = np.load('./../../stats/output/'
                        'meanErrorVSnodes_dorsalEarlyVisualCortex_10neighbor_model5.npz')[
    'list']

tmp = error_map[final_mask_L == 1]
tmp[nodes] = induced_error
error_map[final_mask_L == 1] = tmp + 1
error_map[final_mask_L != 1] = 0

# Location of highest and lowest saliency score
print('Most important vertex is: ' +
      str(nodes[np.where(induced_error == np.max(induced_error))[0]]))

print('Least important vertex is: ' +
      str(nodes[np.where(induced_error == np.min(induced_error))[0]]))

# Predicted map
view = plotting.view_surf(
    surf_mesh=osp.join(osp.dirname(osp.realpath(__file__)), '../../..',
                       'Retinotopy/data/raw/surfaces'
                       '/S1200_7T_Retinotopy181.L.sphere.32k_fs_LR.surf.gii'),
    surf_map=np.reshape(error_map[0:32492], (-1)), bg_map=background,
    cmap='inferno', black_bg=False, symmetric_cmap=False,
    threshold=threshold, vmax=15)
view.open_in_browser()

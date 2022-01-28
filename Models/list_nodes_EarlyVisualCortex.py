import numpy as np

from Retinotopy.functions.plusFovea import add_fovea
from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi

# Generating the list of nodes
# Early visual cortex
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
np.savez('./nodes_earlyVisualCortex.npz', list=nodes)

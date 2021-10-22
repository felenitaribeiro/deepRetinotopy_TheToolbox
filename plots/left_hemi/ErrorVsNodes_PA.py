import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from Retinotopy.functions.plusFovea import add_fovea
from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi
from Retinotopy.functions.def_ROIs_DorsalEarlyVisualCortex import roi as roi2

error = np.load('./../../stats/output/'
              'meanErrorVSnodes_dorsalEarlyVisualCortex_19neighbor_model3.npz')['list']

# TODO - order nodes as function of visual areas
# Generating the list of nodes
# Early visual cortex
early_visual_cortex = ['V1d', 'V1v', 'fovea_V1', 'V2d', 'V2v',
                              'fovea_V2', 'V3d', 'V3v', 'fovea_V3']
V1, V2, V3 = add_fovea(early_visual_cortex)
cluster = np.sum(
    [np.reshape(V1, (-1, 1)), np.reshape(V2, (-1, 1)),
     np.reshape(V3, (-1, 1))], axis=0)
label = ['Early visual cortex']

# ROI
visual_hierarchy = ['ROI']
final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(
    visual_hierarchy)

cluster[V3 == 3] = 3
cluster[V2 == 2] = 2
cluster[V1 == 1] = 1

# dorsal areas
visual_areas = ['ROI']  # TODO
final_mask_L_dorsal, final_mask_R_dorsal, index_L_mask, index_R_mask = roi2(
            visual_areas)
primary_visual_areas = np.zeros((32492, 1))
primary_visual_areas[final_mask_L_dorsal == 1] = 4

final_areas = cluster + primary_visual_areas

V3d_indeces = np.where(final_areas[final_mask_L == 1]==7)[0]
V2d_indeces = np.where(final_areas[final_mask_L == 1]==6)[0]
V1d_indeces = np.where(final_areas[final_mask_L == 1]==5)[0]

V3v_indeces = np.where(final_areas[final_mask_L == 1]==3)[0]
V2v_indeces = np.where(final_areas[final_mask_L == 1]==2)[0]
V1v_indeces = np.where(final_areas[final_mask_L == 1]==1)[0]


ordered_areas = np.concatenate([V1d_indeces, V1v_indeces,
                                V2d_indeces, V2v_indeces,
                                V3d_indeces, V3v_indeces])
# Selecting nodes
nodes = np.load('./../../Models/nodes_earlyVisualCortex.npz')['list']

indeces = []
for i in range(len(nodes)):
    indeces.append(np.where(ordered_areas[i]==nodes)[0][0])

error = error[indeces]

fig, ax = plt.subplots()
ax.stem(np.arange(len(error)), error, linefmt = '#4e4351',markerfmt=' ', bottom=-1)
# ax.axvspan(0, len(V1d_indeces) + len(V1v_indeces), facecolor='#7F508A', alpha = 0.5)
# ax.axvspan(len(V1d_indeces) + len(V1v_indeces), len(V1d_indeces) + len(V1v_indeces) + len(V2d_indeces) + len(V2v_indeces), facecolor='#0078be', alpha = 0.5)
# ax.axvspan(len(V1d_indeces) + len(V1v_indeces) + len(V2d_indeces) + len(V2v_indeces), len(V1d_indeces) + len(V1v_indeces) + len(V2d_indeces) + len(V2v_indeces) + len(V3d_indeces) + len(V3v_indeces), facecolor='#0098b5', alpha = 0.5)

# V1
ax.axvspan(0, len(V1d_indeces), facecolor='#7F508A', alpha = 0.5)
ax.axvspan(len(V1d_indeces), len(V1d_indeces) + len(V1v_indeces), facecolor='#7F508A', alpha = 0.4)
# V2
ax.axvspan(len(V1d_indeces) + len(V1v_indeces), len(V1d_indeces) + len(V1v_indeces) + len(V2d_indeces), facecolor='#6064aa', alpha = 0.5)
ax.axvspan(len(V1d_indeces) + len(V1v_indeces) + len(V2d_indeces), len(V1d_indeces) + len(V1v_indeces) + len(V2d_indeces) + len(V2v_indeces), facecolor='#6064aa', alpha = 0.4)
# V3
ax.axvspan(len(V1d_indeces) + len(V1v_indeces) + len(V2d_indeces) + len(V2v_indeces), len(V1d_indeces) + len(V1v_indeces) + len(V2d_indeces) + len(V2v_indeces) + len(V3d_indeces), facecolor='#0078be', alpha = 0.5)
ax.axvspan(len(V1d_indeces) + len(V1v_indeces) + len(V2d_indeces) + len(V2v_indeces) + len(V3d_indeces), len(V1d_indeces) + len(V1v_indeces) + len(V2d_indeces) + len(V2v_indeces) + len(V3d_indeces) + len(V3v_indeces), facecolor='#0078be', alpha = 0.4)

sns.despine()
plt.ylim(0,20)
plt.xlim(0,len(error))
plt.show()
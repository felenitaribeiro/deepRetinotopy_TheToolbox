import numpy as np
from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi
from Retinotopy.functions.def_ROIs_DorsalEarlyVisualCortex import roi as roi2


# Region of interest used for training
ROI = ['ROI']
final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(
    ROI)
ROI_masked = np.zeros((32492, 1))
ROI_masked[final_mask_L == 1] = 1

# Dorsal V1-V3
final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi2(['ROI'])
dorsal_earlyVisualCortex = np.zeros((32492, 1))
dorsal_earlyVisualCortex[final_mask_L == 1] = 1

# Final mask (selecting dorsal V1-V3 vertices)
mask = ROI_masked + dorsal_earlyVisualCortex
mask = mask[ROI_masked == 1]

# Nodes
np.savez('DorsalEarlyVisualCortex.npz', list=np.where(mask==2)[0].tolist())
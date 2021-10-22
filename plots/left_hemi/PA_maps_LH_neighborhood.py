import numpy as np
import scipy.io
import os.path as osp
import torch

from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi
from nilearn import plotting

subject_index = 7

hcp_id = ['617748', '191336', '572045', '725751', '198653',
          '601127', '644246', '191841', '680957', '157336']

path = './../../Retinotopy/data/raw/converted'
curv = scipy.io.loadmat(osp.join(path, 'cifti_curv_all.mat'))['cifti_curv']
background = np.reshape(
    curv['x' + hcp_id[subject_index] + '_curvature'][0][0][0:32492], (-1))

threshold = 1  # threshold for the curvature map

# Background settings
nocurv = np.isnan(background)
background[nocurv == 1] = 0
background[background < 0] = 0
background[background > 0] = 1

# ROI settings
label_primary_visual_areas = ['ROI']
final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(
    label_primary_visual_areas)

pred = np.zeros((32492, 1))
measured = np.zeros((32492, 1))

# curv_plot = background[final_mask_L == 1] # Plotting the curvature values


# Loading the predictions
predictions = torch.load(
    './../../testset_results/left_hemi'
    '/testset-pred_deepRetinotopy_PA_LH.pt',
    map_location='cpu')

pred[final_mask_L == 1] = np.reshape(
    np.array(predictions['Predicted_values'][subject_index]),
    (-1, 1))

measured[final_mask_L == 1] = np.reshape(
    np.array(predictions['Measured_values'][subject_index]),
    (-1, 1))

# Rescaling
pred = np.array(pred)
minus = pred > 180
sum = pred < 180
pred[minus] = pred[minus] - 180 + threshold
pred[sum] = pred[sum] + 180 + threshold
pred = np.array(pred)

measured = np.array(measured)
minus = measured > 180
sum = measured < 180
measured[minus] = measured[minus] - 180 + threshold
measured[sum] = measured[sum] + 180 + threshold
measured = np.array(measured)

# List of nodes
kernel = np.load('./../../Models/10hops_neighbors_test.npz')['list']
# kernel = np.load('/home/uqfribe1/PycharmProjects/deepRetinotopy_explain'
#                  '/Models/nodes_earlyVisualCortex.npz')['list']
# kernel = [1716, 1717, 1718, 1719, 1720, 1721, 1722, 1723, 1724, 1725, 1726,
#        1757, 1758, 1759, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767,
#        1768, 1788, 1789, 1790, 1791, 1792, 1793, 1794, 1795, 1796, 1797,
#        1798, 1799, 1800, 1801, 1814, 1815, 1816, 1817, 1818, 1819, 1820,
#        1821, 1822, 1823, 1824, 1825, 1826, 1827, 1837, 1838, 1839, 1840,
#        1841, 1842, 1843, 1844, 1845, 1846, 1847, 1848, 1849, 1850, 1851,
#        1858, 1859, 1860, 1861, 1862, 1863, 1864, 1865, 1866, 1867, 1868,
#        1869, 1870, 1871, 1872, 1873, 1877, 1878, 1879, 1880, 1881, 1882,
#        1883, 1884]
transform_kernel = np.where(final_mask_L==1)[0][kernel]

# Neighborhood
new_pred = np.zeros(np.shape(pred))
for i in range(len(pred)):
    if np.sum(transform_kernel==i)!=0:
        new_pred[i][0] = 0
        # print(new_pred[i][0])
    else:
        new_pred[i][0] = pred[i][0]

# Masking
measured[final_mask_L != 1] = 0
pred[final_mask_L != 1] = 0
new_pred[final_mask_L != 1] = 0

# # Empirical map
# view = plotting.view_surf(
#     surf_mesh=osp.join(osp.dirname(osp.realpath(__file__)), '../..',
#                        'Retinotopy/data/raw/surfaces'
#                        '/S1200_7T_Retinotopy181.L.sphere.32k_fs_LR.surf.gii'),
#     surf_map=np.reshape(measured[0:32492], (-1)), bg_map=background,
#     cmap='gist_rainbow_r', black_bg=False, symmetric_cmap=False,
#     threshold=threshold, vmax=361)
# view.open_in_browser()

# Predicted map
view = plotting.view_surf(
    surf_mesh=osp.join(osp.dirname(osp.realpath(__file__)), '../..',
                       'Retinotopy/data/raw/surfaces'
                       '/S1200_7T_Retinotopy181.L.sphere.32k_fs_LR.surf.gii'),
    surf_map=np.reshape(new_pred[0:32492], (-1)), bg_map=background,
    cmap='gist_rainbow_r', black_bg=False, symmetric_cmap=False,
    threshold=threshold, vmax=361)
view.open_in_browser()

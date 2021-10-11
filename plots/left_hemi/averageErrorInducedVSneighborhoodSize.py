import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from Retinotopy.functions.def_ROIs_DorsalEarlyVisualCortex import roi as roi2
from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi
from Retinotopy.functions.plusFovea import add_fovea

models = np.arange(1, 16, 1)
for j in models:
    error_matrix = []
    for i in range(10):
        error_matrix.append(np.load('./../../stats/output/'
                                    'meanErrorVSnodes_dorsalEarlyVisualCortex_'
                                    + str(
            i + 1) + 'neighbor_model3.npz')['list'])

    error_matrix = np.array(error_matrix).T
    error_matrix = np.reshape(error_matrix, (-1, 10))

    # Dorsal V1-V3
    final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi2(
        ['ROI'])
    areas = np.zeros((32492, 1))
    areas[final_mask_L == 1] = 1
    nodes = areas[final_mask_L == 1]
    nodes_dorsalV123 = np.where(nodes != 0)[0]

    error_matrix_dorsalV123 = error_matrix[nodes_dorsalV123]
    means = np.mean(error_matrix_dorsalV123, axis = 0)

    data = pd.DataFrame(columns=['Error', 'Model', 'Neighborhood'])
    data_tmp = pd.DataFrame({'Error': means, 'Model': 10 * ['model_' + str(j)],
                             'Neighborhood': np.arange(1, 16)})
    data = data.append(data_tmp, ignore_index=True)

# means = np.mean(error_matrix_dorsalV123, axis = 0)
# stds = np.std(error_matrix_dorsalV123, axis = 0)


plt.plot(np.arange(1, 11), means)
plt.fill_between(np.arange(1, 11), means - stds, means + stds, alpha=.1)
# sns.lineplot(error_matrix_dorsalV123)
plt.show()

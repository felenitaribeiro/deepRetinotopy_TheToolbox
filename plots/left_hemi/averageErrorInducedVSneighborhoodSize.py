import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from Retinotopy.functions.def_ROIs_DorsalEarlyVisualCortex import roi as roi2
from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi
from Retinotopy.functions.plusFovea import add_fovea

models = np.arange(1, 6, 1)
data = pd.DataFrame(columns=['Error', 'Model', 'Neighborhood'])
max_neighborhood = 20
for j in models:
    error_matrix = []
    error_matrix_reversed = []
    for i in range(max_neighborhood):
        error_matrix.append(np.load('./../../stats/output/'
                                    'meanErrorVSnodes_dorsalEarlyVisualCortex_'
                                    + str(
            i + 1) + 'neighbor_model' + str(j) + '.npz')['list'])
        error_matrix_reversed.append(np.load('./../../stats/output/'
                                    'meanErrorVSnodes_dorsalEarlyVisualCortex_'
                                    + str(
            i + 1) + 'neighbor_reversed_model' + str(j) + '.npz')['list'])


    error_matrix = np.array(error_matrix).T
    error_matrix = np.reshape(error_matrix, (-1, max_neighborhood))

    error_matrix_reversed = np.array(error_matrix_reversed).T
    error_matrix_reversed = np.reshape(error_matrix_reversed, (-1, max_neighborhood))

    # Dorsal V1-V3
    final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi2(
        ['ROI'])
    areas = np.zeros((32492, 1))
    areas[final_mask_L == 1] = 1
    nodes = areas[final_mask_L == 1]
    nodes_dorsalV123 = np.where(nodes != 0)[0]

    error_matrix_dorsalV123 = error_matrix[nodes_dorsalV123]
    error_matrix_dorsalV123_reversed = error_matrix_reversed[nodes_dorsalV123]

    means = np.mean(error_matrix_dorsalV123, axis = 0)
    means_reversed = np.mean(error_matrix_dorsalV123_reversed, axis=0)

    data_tmp = pd.DataFrame({'Error': means, 'Model': max_neighborhood * ['model_' + str(j)],
                             'Neighborhood': np.arange(1, max_neighborhood + 1), 'Patch': max_neighborhood * ['inner']})
    data = data.append(data_tmp, ignore_index=True)

    data_tmp = pd.DataFrame({'Error': means_reversed, 'Model': max_neighborhood * ['model_' + str(j)],
                             'Neighborhood': np.arange(1, max_neighborhood + 1), 'Patch': max_neighborhood * ['outer']})
    data = data.append(data_tmp, ignore_index=True)

# means = np.mean(error_matrix_dorsalV123, axis = 0)
# stds = np.std(error_matrix_dorsalV123, axis = 0)
# data.to_excel('data', data)
plot = sns.lineplot(data=data, x="Neighborhood", y="Error", hue='Patch')
plot.set_xticks(np.arange(0,21, 2))

# plt.plot(np.arange(1, 11), means)
# plt.fill_between(np.arange(1, 11), means - stds, means + stds, alpha=.1)
# sns.lineplot(error_matrix_dorsalV123)
plt.show()
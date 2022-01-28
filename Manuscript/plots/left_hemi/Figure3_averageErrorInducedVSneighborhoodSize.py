import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from Retinotopy.functions.def_ROIs_DorsalEarlyVisualCortex import roi as roi2
from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi
from Retinotopy.functions.plusFovea import add_fovea

data = pd.DataFrame(columns=['Saliency', 'Nodes', 'Neighborhood', 'Region'])
max_neighborhood = 20

error_matrix = []
error_matrix_reversed = []
neighborhood = []
for i in range(max_neighborhood):
    error_matrix.append(np.load('./../../stats/output/'
                                'meanErrorVSnodes_dorsalEarlyVisualCortex_'
                                + str(
        i + 1) + 'neighbor_model5.npz')['list'])
    error_matrix_reversed.append(np.load('./../../stats/output/'
                                         'meanErrorVSnodes_dorsalEarlyVisualCortex_'
                                         + str(
        i + 1) + 'neighbor_reversed_model5.npz')['list'])

error_matrix = np.array(error_matrix).T
error_matrix = np.reshape(error_matrix, (-1, max_neighborhood))

error_matrix_reversed = np.array(error_matrix_reversed).T
error_matrix_reversed = np.reshape(error_matrix_reversed,
                                   (-1, max_neighborhood))

# Dorsal V1-V3
final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi2(
    ['ROI'])
areas = np.zeros((32492, 1))
areas[final_mask_L == 1] = 1
nodes = areas[final_mask_L == 1]
nodes_dorsalV123 = np.where(nodes != 0)[0]

error_matrix_dorsalV123 = error_matrix[nodes_dorsalV123]
error_matrix_dorsalV123_reversed = error_matrix_reversed[nodes_dorsalV123]

nodes_scores = error_matrix_dorsalV123.T.flatten()
nodes_scores_reversed = error_matrix_dorsalV123_reversed.T.flatten()

neighborhood = [[i] * np.shape(error_matrix_dorsalV123)[0] for i in
                range(1, 21)]

nodes_ref = [np.arange(
    np.shape(error_matrix_dorsalV123)[0])] * max_neighborhood
print(nodes_ref)
nodes_ref = np.array(nodes_ref).flatten()

# means = np.mean(error_matrix_dorsalV123, axis=0)
# means_reversed = np.mean(error_matrix_dorsalV123_reversed, axis=0)

data_tmp = pd.DataFrame(
    {'Saliency': nodes_scores, 'Nodes': nodes_ref,
     'Neighborhood': np.array(neighborhood).flatten(),
     'Region': max_neighborhood * ['inner'] *
               np.shape(error_matrix_dorsalV123)[
                   0]})
data = data.append(data_tmp, ignore_index=True)

data_tmp = pd.DataFrame({'Saliency': nodes_scores_reversed,
                         'Nodes': nodes_ref,
                         'Neighborhood': np.array(neighborhood).flatten(),
                         'Region': max_neighborhood * ['outer'] *
                                   np.shape(error_matrix_dorsalV123)[0]})
data = data.append(data_tmp, ignore_index=True)

palette_1 = [sns.color_palette("PRGn_r")[5],
             sns.color_palette("PRGn_r")[0]]
palette_1 = ['#19adaf', '#5865a2']

sns.set_style("ticks")
plot = sns.lineplot(data=data, x="Neighborhood", y="Saliency", hue='Region',
                    palette=palette_1)
plot.set_xticks(np.arange(0, 21, 2))
plt.xlim(1, 20)
plt.ylim(0, 20)
# plt.vlines(19, 0, 16, 'tab:gray' ,'dashed')
# plt.plot(np.arange(1, 11), means)
# plt.fill_between(np.arange(1, 11), means - stds, means + stds, alpha=.1)
# sns.lineplot(error_matrix_dorsalV123)
sns.despine()
plt.savefig('fig3.svg')
plt.show()

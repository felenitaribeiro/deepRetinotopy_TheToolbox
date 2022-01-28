import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from Retinotopy.functions.def_ROIs_DorsalEarlyVisualCortex import roi as roi2
from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi
from Retinotopy.functions.plusFovea import add_fovea

data = pd.DataFrame(columns=['Saliency', 'Nodes', 'Neighborhood', 'Feature'])

neighborhoods = [5, 10, 15, 20]
features = ['both', 'curvature', 'myelin']

for feature in features:
    error_matrix = []
    neighborhood = []
    for i in neighborhoods:
        if feature == 'both':
            error_matrix.append(np.load('./../../stats/output/'
                                        'meanErrorVSnodes_dorsalEarlyVisualCortex_'
                                        + str(
                i) + 'neighbor_model5.npz')['list'])
        else:
            error_matrix.append(np.load('./../../stats/output/'
                                        'meanErrorVSnodes_dorsalEarlyVisualCortex_'
                                        + str(
                i) + 'neighbor_' + feature + '_model5.npz')['list'])

    error_matrix = np.array(error_matrix).T
    error_matrix = np.reshape(error_matrix, (-1, len(neighborhoods)))

    # Dorsal V1-V3
    final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi2(
        ['ROI'])
    areas = np.zeros((32492, 1))
    areas[final_mask_L == 1] = 1
    nodes = areas[final_mask_L == 1]
    nodes_dorsalV123 = np.where(nodes != 0)[0]

    error_matrix_dorsalV123 = error_matrix[nodes_dorsalV123]

    nodes_scores = error_matrix_dorsalV123.T.flatten()

    neighborhood = [[i] * np.shape(error_matrix_dorsalV123)[0] for i in
                    neighborhoods]

    nodes_ref = [np.arange(
        np.shape(error_matrix_dorsalV123)[0])] * len(neighborhoods)
    nodes_ref = np.array(nodes_ref).flatten()

    data_tmp = pd.DataFrame(
        {'Saliency': nodes_scores, 'Nodes': nodes_ref,
         'Neighborhood': np.array(neighborhood).flatten(),
         'Feature': len(neighborhoods) * [feature] *
                    np.shape(error_matrix_dorsalV123)[
                        0]})
    data = data.append(data_tmp, ignore_index=True)

palette_1 = ['#19adaf', '#2289ca', '#975096']

sns.set_style("ticks")
plot = sns.barplot(data=data, x="Neighborhood", y="Saliency", hue='Feature',
                   palette=palette_1)
sns.despine()
plt.savefig('fig4.svg')
plt.show()

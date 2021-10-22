import numpy as np
import os
import matplotlib.pyplot as plt


def reliabity_corrMatrix():
    """Determines the correlation between error maps generated with different models.

    Args: #TODO
        model (str): 'deepRetinotopy' or 'average' or 'Benson14'

    Output: #TODO
        .npz files in ./../output named:
        'ErrorPerParticipant_PA_LH_WangParcels_' + str(model) + '_1-8.npz'
        'ErrorPerParticipant_PA_LH_EarlyVisualCortex_' + str(model) +
        '_1-8.npz'
        'ErrorPerParticipant_PA_LH_dorsalV1-3_' + str(model) + '_1-8.npz'

    """
    corrMatrix = np.zeros((5,5))
    for i in range(5):
        for j in range(5):
            error_1 = np.load('./../output/'
                        'meanErrorVSnodes_dorsalEarlyVisualCortex_10neighbor_model'+ str(i+1) +'.npz')[
            'list']
            error_2 = np.load('./../output/'
                        'meanErrorVSnodes_dorsalEarlyVisualCortex_10neighbor_model'+ str(j+1) +'.npz')[
            'list']
            corrMatrix[i,j] = np.corrcoef(error_1.flatten(), error_2.flatten())[0][1]

    return corrMatrix

# Create an output folder if it doesn't already exist
directory = './../output'
if not os.path.exists(directory):
    os.makedirs(directory)

corrMatrix = reliabity_corrMatrix()

fig = plt.imshow(corrMatrix, vmin= 0.75, vmax=1, cmap = 'viridis_r')
plt.colorbar(fig)
plt.show()
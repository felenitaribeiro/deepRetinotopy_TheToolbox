import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd

def reliabity_corrMatrix(feature):
    """Determines the correlation between saliency maps generated
    with different models.

    Args:
        Feature (str): Occluded feature: 'both', 'myelin' or 'curvature'.
    Output:
        corrMatrix (numpy array); Correlation matrix (5,5)

    """
    corrMatrix = np.zeros((5,5))
    for i in range(5):
        for j in range(5):
            if feature == 'both':
                error_1 = np.load('./../../stats/output/'
                            'meanErrorVSnodes_dorsalEarlyVisualCortex_10neighbor_model'+ str(i+1) +'.npz')[
                'list']
                error_2 = np.load('./../../stats/output/'
                            'meanErrorVSnodes_dorsalEarlyVisualCortex_10neighbor_model'+ str(j+1) +'.npz')[
                'list']
                corrMatrix[i,j] = np.corrcoef(error_1.flatten(), error_2.flatten())[0][1]
            else:
                error_1 = np.load('./../../stats/output/'
                                  'meanErrorVSnodes_dorsalEarlyVisualCortex_10neighbor_' + feature + '_model' + str(
                    i + 1) + '.npz')[
                    'list']
                error_2 = np.load('./../../stats/output/'
                                  'meanErrorVSnodes_dorsalEarlyVisualCortex_10neighbor_' + feature + '_model' + str(
                    j + 1) + '.npz')[
                    'list']
                corrMatrix[i, j] = \
                np.corrcoef(error_1.flatten(), error_2.flatten())[0][1]

    return corrMatrix

# Create an output folder if it doesn't already exist
directory = './../../../stats/output'
if not os.path.exists(directory):
    os.makedirs(directory)

features = ['both', 'curvature', 'myelin']
data = pd.DataFrame(columns=['Feature', 'Mean', 'SD'])
for feature in features:
    corrMatrix = reliabity_corrMatrix(feature)

    # # To visualize correlation matrix
    # fig = plt.imshow(corrMatrix, vmin= 0.5, vmax=1, cmap = 'viridis_r')
    # plt.xticks(np.arange(0,5),np.arange(1,6))
    # plt.yticks(np.arange(0,5),np.arange(1,6))
    # plt.xlabel('Model')
    # plt.ylabel('Model')
    # plt.colorbar(fig)
    # plt.title('Correlation scores')
    # plt.savefig('realiabilityMatrix_'+ feature + '.svg')
    # plt.show()

    corrMatrix = np.triu(corrMatrix, k=1)[np.triu(corrMatrix, k=1)!=0]
    tmp = pd.DataFrame({'Feature': [str(feature)],
                        'Mean': [np.mean(corrMatrix)],
                        'SD': [np.std(corrMatrix)]})
    data = data.append(tmp)

print(data)
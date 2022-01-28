import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

models = np.arange(1, 6, 1)
data = pd.DataFrame(columns=['Error', 'Model', 'Neighborhood'])
normalization = ['None', '10', '50', '100', '500', '1000']
for j in models:
    error_matrix = []
    error_matrix.append(np.load(
        './../../stats/output_norm'
        '/meanErrorVSnormalization_dorsalEarlyVisualCortex_norm_model' + str(
            j) + '.npz')['list'])
    print(error_matrix)

    error_matrix = np.reshape(error_matrix, (1, len(normalization)))
    print(error_matrix[0])

    data_tmp = pd.DataFrame({'Error': error_matrix[0],
                             'Model': len(normalization) * ['model_' + str(j)],
                             'Normalization': normalization})
    data = data.append(data_tmp, ignore_index=True)

plot = sns.lineplot(data=data, x="Normalization", y="Error")
plt.show()

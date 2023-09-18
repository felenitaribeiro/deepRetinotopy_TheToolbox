import os
import os.path as osp
import torch
import torch.nn.functional as F
import torch_geometric.transforms as T
import sys

sys.path.append('..')

from utils.HCP_3sets_ROI import Retinotopy
from torch_geometric.data import DataLoader
from torch_geometric.nn import SplineConv
from utils.model import deepRetinotopy

path = osp.join(osp.dirname(osp.realpath(__file__)), '../../Retinotopy',
                'data')
pre_transform = T.Compose([T.FaceToEdge()])
hemisphere = 'Left'  # or 'Right'
norm_value = 70.4237

# Loading test dataset
dev_dataset = Retinotopy(path, 'Development',
                         transform=T.Cartesian(max_value=norm_value),
                         pre_transform=pre_transform, n_examples=181,
                         prediction='polarAngle', myelination=True,
                         hemisphere=hemisphere)
dev_loader = DataLoader(dev_dataset, batch_size=1, shuffle=False)
test_dataset = Retinotopy(path, 'Test',
                          transform=T.Cartesian(max_value=norm_value),
                          pre_transform=pre_transform, n_examples=181,
                          prediction='polarAngle', myelination=True,
                          hemisphere=hemisphere)
test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)



for i in range(5):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = deepRetinotopy(num_features=2).to(device)
    model.load_state_dict(
        torch.load(
            './../output/deepRetinotopy_PA_LH_model' + str(i + 1) + '.pt',
            map_location=device))

    # Create an output folder if it doesn't already exist
    directory = './devset_results'
    if not osp.exists(directory):
        os.makedirs(directory)


    def test():
        model.eval()
        MeanAbsError = 0
        y = []
        y_hat = []
        for data in dev_loader:
            pred = model(data.to(device)).detach()
            y_hat.append(pred)
            y.append(data.to(device).y.view(-1))
            MAE = torch.mean(abs(data.to(device).y.view(-1) - pred)).item()
            MeanAbsError += MAE
        test_MAE = MeanAbsError / len(dev_loader)
        output = {'Predicted_values': y_hat, 'Measured_values': y,
                  'MAE': test_MAE}
        return output


    evaluation = test()

    torch.save({'Predicted_values': evaluation['Predicted_values'],
                'Measured_values': evaluation['Measured_values']},
               osp.join(osp.dirname(osp.realpath(__file__)),
                        'devset_results',
                        'devset-intactData_model' + str(
                            i + 1) + '.pt'))

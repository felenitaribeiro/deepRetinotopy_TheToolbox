import os
import os.path as osp
import torch
import torch.nn.functional as F
import torch_geometric.transforms as T
import sys
import numpy as np

sys.path.append('../..')

from Retinotopy.dataset.HCP_3sets_ROI import Retinotopy
from torch_geometric.data import DataLoader
from torch_geometric.nn import SplineConv
from Retinotopy.functions.neighborhood import node_neighbourhood

path = osp.join(osp.dirname(osp.realpath(__file__)), '../Retinotopy', 'data')
pre_transform = T.Compose([T.FaceToEdge()])

hemisphere = 'Left'  # or 'Right'
# Loading test dataset
test_dataset = Retinotopy(path, 'Test', transform=T.Cartesian(),
                          pre_transform=pre_transform, n_examples=181,
                          prediction='polarAngle', myelination=True,
                          hemisphere=hemisphere)
test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)

nodes = np.load('nodes_earlyVisualCortex.npz')['list']
neighborhood_size = 5


# Model
class Net(torch.nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = SplineConv(2, 8, dim=3, kernel_size=25, norm=False)
        self.bn1 = torch.nn.BatchNorm1d(8)

        self.conv2 = SplineConv(8, 16, dim=3, kernel_size=25, norm=False)
        self.bn2 = torch.nn.BatchNorm1d(16)

        self.conv3 = SplineConv(16, 32, dim=3, kernel_size=25, norm=False)
        self.bn3 = torch.nn.BatchNorm1d(32)

        self.conv4 = SplineConv(32, 32, dim=3, kernel_size=25, norm=False)
        self.bn4 = torch.nn.BatchNorm1d(32)

        self.conv5 = SplineConv(32, 32, dim=3, kernel_size=25, norm=False)
        self.bn5 = torch.nn.BatchNorm1d(32)

        self.conv6 = SplineConv(32, 32, dim=3, kernel_size=25, norm=False)
        self.bn6 = torch.nn.BatchNorm1d(32)

        self.conv7 = SplineConv(32, 32, dim=3, kernel_size=25, norm=False)
        self.bn7 = torch.nn.BatchNorm1d(32)

        self.conv8 = SplineConv(32, 32, dim=3, kernel_size=25, norm=False)
        self.bn8 = torch.nn.BatchNorm1d(32)

        self.conv9 = SplineConv(32, 32, dim=3, kernel_size=25, norm=False)
        self.bn9 = torch.nn.BatchNorm1d(32)

        self.conv10 = SplineConv(32, 16, dim=3, kernel_size=25, norm=False)
        self.bn10 = torch.nn.BatchNorm1d(16)

        self.conv11 = SplineConv(16, 8, dim=3, kernel_size=25, norm=False)
        self.bn11 = torch.nn.BatchNorm1d(8)

        self.conv12 = SplineConv(8, 1, dim=3, kernel_size=25, norm=False)

    def forward(self, data):
        x, edge_index, pseudo = data.x, data.edge_index, data.edge_attr
        x = F.elu(self.conv1(x, edge_index, pseudo))
        x = self.bn1(x)
        x = F.dropout(x, p=.10, training=self.training)

        x = F.elu(self.conv2(x, edge_index, pseudo))
        x = self.bn2(x)
        x = F.dropout(x, p=.10, training=self.training)

        x = F.elu(self.conv3(x, edge_index, pseudo))
        x = self.bn3(x)
        x = F.dropout(x, p=.10, training=self.training)

        x = F.elu(self.conv4(x, edge_index, pseudo))
        x = self.bn4(x)
        x = F.dropout(x, p=.10, training=self.training)

        x = F.elu(self.conv5(x, edge_index, pseudo))
        x = self.bn5(x)
        x = F.dropout(x, p=.10, training=self.training)

        x = F.elu(self.conv6(x, edge_index, pseudo))
        x = self.bn6(x)
        x = F.dropout(x, p=.10, training=self.training)

        x = F.elu(self.conv7(x, edge_index, pseudo))
        x = self.bn7(x)
        x = F.dropout(x, p=.10, training=self.training)

        x = F.elu(self.conv8(x, edge_index, pseudo))
        x = self.bn8(x)
        x = F.dropout(x, p=.10, training=self.training)

        x = F.elu(self.conv9(x, edge_index, pseudo))
        x = self.bn9(x)
        x = F.dropout(x, p=.10, training=self.training)

        x = F.elu(self.conv10(x, edge_index, pseudo))
        x = self.bn10(x)
        x = F.dropout(x, p=.10, training=self.training)

        x = F.elu(self.conv11(x, edge_index, pseudo))
        x = self.bn11(x)
        x = F.dropout(x, p=.10, training=self.training)

        x = F.elu(self.conv12(x, edge_index, pseudo)).view(-1)
        return x


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = Net().to(device)
model.load_state_dict(torch.load('./deepRetinotopy_PA_LH_model.pt',
                                 map_location=device))

# Create an output folder if it doesn't already exist
directory = './devset_results'
if not osp.exists(directory):
    os.makedirs(directory)

for node in nodes:
    def test():
        model.eval()
        MeanAbsError = 0
        y = []
        y_hat = []
        for data in test_loader:
            new_data, _ = node_neighbourhood(data, node, neighborhood_size)
            pred = model(new_data.to(device)).detach()
            y_hat.append(pred)
            y.append(data.to(device).y.view(-1))
            MAE = torch.mean(abs(data.to(device).y.view(-1) - pred)).item()
            MeanAbsError += MAE
        test_MAE = MeanAbsError / len(test_loader)
        output = {'Predicted_values': y_hat, 'Measured_values': y,
                  'MAE': test_MAE}
        return output


    evaluation = test()

    torch.save({'Predicted_values': evaluation['Predicted_values'],
                'Measured_values': evaluation['Measured_values']},
               osp.join(osp.dirname(osp.realpath(__file__)), 'devset_results',
                        'testset-node' + str(node) + '_neighborhood' + str(
                            neighborhood_size) + '.pt'))

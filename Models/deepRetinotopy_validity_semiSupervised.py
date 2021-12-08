import os
import os.path as osp
import torch
import torch.nn.functional as F
import torch_geometric.transforms as T
import sys
import numpy as np
import time

sys.path.append('..')

from Retinotopy.dataset.HCP_3sets_ROI import Retinotopy
from torch_geometric.data import DataLoader
from torch_geometric.nn import SplineConv

path = osp.join(osp.dirname(osp.realpath(__file__)), '..', 'Retinotopy',
                'data')
pre_transform = T.Compose([T.FaceToEdge()])
norm_value = 70.4237

train_dataset = Retinotopy(path, 'Train',
                           transform=T.Cartesian(max_value=norm_value),
                           pre_transform=pre_transform, n_examples=181,
                           prediction='polarAngle', myelination=True,
                           hemisphere='Left')  # Change to Right for the RH
dev_dataset = Retinotopy(path, 'Development',
                         transform=T.Cartesian(max_value=norm_value),
                         pre_transform=pre_transform, n_examples=181,
                         prediction='polarAngle', myelination=True,
                         hemisphere='Left')  # Change to Right for the RH
train_loader = DataLoader(train_dataset, batch_size=1, shuffle=True)
dev_loader = DataLoader(dev_dataset, batch_size=1, shuffle=False)

# Patch
kernel = np.load('./DorsalEarlyVisualCortex.npz')['list']
ROIminusPatch = [item for item in np.arange(0, 3267) if item not in kernel]


# Model
class Net(torch.nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = SplineConv(2, 8, dim=3, kernel_size=25)
        self.bn1 = torch.nn.BatchNorm1d(8)

        self.conv2 = SplineConv(8, 16, dim=3, kernel_size=25)
        self.bn2 = torch.nn.BatchNorm1d(16)

        self.conv3 = SplineConv(16, 32, dim=3, kernel_size=25)
        self.bn3 = torch.nn.BatchNorm1d(32)

        self.conv4 = SplineConv(32, 32, dim=3, kernel_size=25)
        self.bn4 = torch.nn.BatchNorm1d(32)

        self.conv5 = SplineConv(32, 32, dim=3, kernel_size=25)
        self.bn5 = torch.nn.BatchNorm1d(32)

        self.conv6 = SplineConv(32, 32, dim=3, kernel_size=25)
        self.bn6 = torch.nn.BatchNorm1d(32)

        self.conv7 = SplineConv(32, 32, dim=3, kernel_size=25)
        self.bn7 = torch.nn.BatchNorm1d(32)

        self.conv8 = SplineConv(32, 32, dim=3, kernel_size=25)
        self.bn8 = torch.nn.BatchNorm1d(32)

        self.conv9 = SplineConv(32, 32, dim=3, kernel_size=25)
        self.bn9 = torch.nn.BatchNorm1d(32)

        self.conv10 = SplineConv(32, 16, dim=3, kernel_size=25)
        self.bn10 = torch.nn.BatchNorm1d(16)

        self.conv11 = SplineConv(16, 8, dim=3, kernel_size=25)
        self.bn11 = torch.nn.BatchNorm1d(8)

        self.conv12 = SplineConv(8, 1, dim=3, kernel_size=25)

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
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)


def train(epoch):
    model.train()

    if epoch == 100:
        for param_group in optimizer.param_groups:
            param_group['lr'] = 0.005

    for data in train_loader:
        data = data.to(device)
        optimizer.zero_grad()

        R2 = data.R2.view(-1)
        threshold = R2.view(-1) > 2.2

        loss = torch.nn.SmoothL1Loss()
        output_loss = loss(R2[ROIminusPatch] * model(data)[ROIminusPatch],
                           R2[ROIminusPatch] * data.y.view(-1)[ROIminusPatch])
        output_loss.backward()

        MAE = torch.mean(abs(
            data.to(device).y.view(-1)[threshold == 1] - model(data)[
                threshold == 1])).item()  # To check the performance of the
        # model while training

        optimizer.step()
    return output_loss.detach(), MAE


def test():
    model.eval()

    MeanAbsError = 0
    MeanAbsError_thr = 0
    y = []
    y_hat = []
    R2_plot = []

    for data in dev_loader:
        pred = model(data.to(device)).detach()
        y_hat.append(pred)
        y.append(data.to(device).y.view(-1))

        R2 = data.R2.view(-1)
        R2_plot.append(R2)
        threshold = R2.view(-1) > 2.2
        threshold2 = R2.view(-1) > 17

        MAE = torch.mean(abs(data.to(device).y.view(-1)[threshold == 1] - pred[
            threshold == 1])).item()  # To check the performance of the
        # model while training
        MAE_thr = torch.mean(abs(
            data.to(device).y.view(-1)[threshold2 == 1] - pred[
                threshold2 == 1])).item()  # To check the performance of the
        # model while training
        MeanAbsError_thr += MAE_thr
        MeanAbsError += MAE

    test_MAE = MeanAbsError / len(dev_loader)
    test_MAE_thr = MeanAbsError_thr / len(dev_loader)
    output = {'Predicted_values': y_hat, 'Measured_values': y, 'R2': R2_plot,
              'MAE': test_MAE, 'MAE_thr': test_MAE_thr}
    return output


# init = time.time() # To find out how long it takes to train the model

# Create an output folder if it doesn't already exist
directory = './output'
if not osp.exists(directory):
    os.makedirs(directory)

# Model training
for i in range(5):
    for epoch in range(1, 201):
        loss, MAE = train(epoch)
        test_output = test()
        print(
            'Epoch: {:02d}, Train_loss: {:.4f}, Train_MAE: {:.4f}, Test_MAE: '
            '{:.4f}, Test_MAE_thr: {:.4f}'.format(
                epoch, loss, MAE, test_output['MAE'], test_output['MAE_thr']))
        # if epoch % 25 == 0:  # To save intermediate predictions
        #     torch.save({'Epoch': epoch,
        #                 'Predicted_values': test_output['Predicted_values'],
        #                 'Measured_values': test_output['Measured_values'],
        #                 'R2': test_output['R2'], 'Loss': loss,
        #                 'Dev_MAE': test_output['MAE']},
        #                osp.join(osp.dirname(osp.realpath(__file__)),
        #                         'output',
        #                         'deepRetinotopy_PA_LH_output_epoch' + str(
        #                             epoch) + '.pt')) # Rename if RH

    # Saving model's learned parameters
    torch.save(model.state_dict(),
               osp.join(osp.dirname(osp.realpath(__file__)), 'output',
                        'deepRetinotopy_PA_LH_model' + str(
                            i + 1) + '_ROIminusPatch.pt'))  # Rename if RH

# end = time.time() # To find out how long it takes to train the model
# time = (end - init) / 60
# print(str(time) + ' minutes')

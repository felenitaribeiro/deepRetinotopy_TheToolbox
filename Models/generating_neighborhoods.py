import os.path as osp
import torch_geometric.transforms as T
import sys
import numpy as np

sys.path.append('..')

from Retinotopy.dataset.HCP_3sets_ROI import Retinotopy
from torch_geometric.data import DataLoader
from Retinotopy.functions.neighborhood import node_neighbourhood

path = osp.join(osp.dirname(osp.realpath(__file__)), '..', 'Retinotopy', 'data')

pre_transform = T.Compose([T.FaceToEdge()])

dev_dataset = Retinotopy(path, 'Development', transform=T.Cartesian(),
                         pre_transform=pre_transform, n_examples=181,
                         prediction='polarAngle', myelination=True,
                         hemisphere='Left') # Change to Right for the RH
dev_loader = DataLoader(dev_dataset, batch_size=1, shuffle=False)

for data in dev_loader:
    new_data, _ = node_neighbourhood(data, 1792, 10)

np.savez('10hops_neighbors_test.npz', list=_['level_10'].tolist())
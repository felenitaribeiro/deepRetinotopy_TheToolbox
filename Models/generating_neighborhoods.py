import os.path as osp
import torch_geometric.transforms as T
import sys

sys.path.append('..')

from Retinotopy.dataset.HCP_3sets_ROI import Retinotopy
from torch_geometric.data import DataLoader
from Explainability.neighborhood import node_neighbourhood

path = osp.join(osp.dirname(osp.realpath(__file__)), '..', 'Retinotopy',
                'data')
norm_value = 70.4237
pre_transform = T.Compose([T.FaceToEdge()])

dev_dataset = Retinotopy(path, 'Development',
                         transform=T.Cartesian(max_value=norm_value),
                         pre_transform=pre_transform, n_examples=181,
                         prediction='polarAngle', myelination=True,
                         hemisphere='Left')  # Change to Right for the RH
dev_loader = DataLoader(dev_dataset, batch_size=1, shuffle=False)

for data in dev_loader:
    new_data, _ = node_neighbourhood(data, 2162, 20)
    # least 2562
    # most 1982
    # 2162 for figures
# np.savez('18hops_figure3.npz', list=_['level_18'].tolist())

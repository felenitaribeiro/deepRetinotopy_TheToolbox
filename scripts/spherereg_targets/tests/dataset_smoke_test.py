"""Build Retinotopy(dataset='HCP_spherereg') end-to-end and check split sizes."""
import sys, os.path as osp
TOOLBOX='/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox'
sys.path.insert(0, TOOLBOX)
import torch_geometric.transforms as T
from utils.dataset import Retinotopy

root = f'{TOOLBOX}/sandbox/spherereg_targets/loader_test/HCP_new'
subs = [s.strip() for s in open(f'{TOOLBOX}/sandbox/spherereg_targets/subjects.txt') if s.strip()]
pre = T.Compose([T.FaceToEdge()])
for s in ['Train', 'Development', 'Test']:
    ds = Retinotopy(root, s, transform=T.Cartesian(max_value=10),
                    pre_transform=pre, dataset='HCP_spherereg', list_subs=list(subs),
                    prediction='polarAngle', hemisphere='Left', shuffle=True,
                    stimulus='original', roi_name='wholebrain', myelination=False)
    d = ds[0]
    print(f'{s}: n={len(ds)} x{tuple(d.x.shape)} y{tuple(d.y.shape)} edges{tuple(d.edge_index.shape)} mask={int(d.mask.sum())}')
print('smoke test PASS')

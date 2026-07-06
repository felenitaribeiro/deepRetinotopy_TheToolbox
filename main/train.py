import os
import os.path as osp
import torch
from torch.optim.swa_utils import AveragedModel, SWALR, update_bn
from torch.optim.lr_scheduler import CosineAnnealingLR
import torch_geometric.transforms as T
import sys
import time
import argparse
import json
import subprocess
import datetime
import torch.nn.functional as F
from torch_geometric.loader import DataLoader

sys.path.append('..')

from utils.model import deepRetinotopy
from utils.dataset import Retinotopy

EPS = 1e-8


def _weighted_mean(per_vertex, weight):
    return (weight * per_vertex).sum() / (weight.sum() + EPS)


def loss_euclidean(pred, target, R2, mask):
    """R2-weighted mean Euclidean distance in Cartesian visual-field space."""
    dist = torch.sqrt(((pred - target) ** 2).sum(dim=1) + 1e-12)
    return _weighted_mean(dist, R2 * mask.float())


def loss_mse(pred, target, R2, mask):
    """R2-weighted mean squared error on (x, y). Up-weights large (peripheral)
    errors relative to the plain distance."""
    se = ((pred - target) ** 2).sum(dim=1)
    return _weighted_mean(se, R2 * mask.float())


def loss_smoothl1(pred, target, R2, mask):
    """R2-weighted Smooth-L1 (Huber) on the 2D residual; robust to outliers."""
    per = F.smooth_l1_loss(pred, target, reduction='none').sum(dim=1)
    return _weighted_mean(per, R2 * mask.float())


def loss_ecc_weighted(pred, target, R2, mask):
    """R2-weighted Euclidean distance, additionally weighted by empirical
    eccentricity (normalized radius) to push the model to fit the periphery."""
    dist = torch.sqrt(((pred - target) ** 2).sum(dim=1) + 1e-12)
    r_emp = torch.sqrt((target ** 2).sum(dim=1) + 1e-12)  # normalized ecc in [0, 1]
    return _weighted_mean(dist, R2 * mask.float() * r_emp)


LOSSES = {
    'euclidean': loss_euclidean,
    'mse': loss_mse,
    'smoothl1': loss_smoothl1,
    'ecc_weighted': loss_ecc_weighted,
}


def _git_info(repo):
    def run(cmd):
        try:
            return subprocess.check_output(cmd, cwd=repo,
                                           stderr=subprocess.DEVNULL).decode().strip()
        except Exception:
            return 'unknown'
    sha = run(['git', 'rev-parse', 'HEAD'])
    dirty = run(['git', 'status', '--porcelain'])
    return sha, (dirty not in ('', 'unknown'))


def train(epoch, model, optimizer, train_loader, device, coords=False, loss_fn=None,
          grad_clip=0.0, step_lr=True):
    model.train()

    if step_lr and epoch == 100:
        for param_group in optimizer.param_groups:
            param_group['lr'] = param_group['lr'] * 0.5

    for data in train_loader:
        data = data.to(device)
        optimizer.zero_grad()

        R2 = data.R2.view(-1)

        if coords:
            pred = model(data)                       # (N, 2)
            target = data.y                          # (N, 2)
            mask = data.mask.view(-1)
            output_loss = loss_fn(pred, target, R2, mask)
            output_loss.backward()
            if grad_clip:
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            optimizer.step()
            with torch.no_grad():
                dist = torch.sqrt(((pred - target) ** 2).sum(dim=1) + 1e-12)
                thr = (R2 > 2.2) & mask
                # Mean Euclidean distance in degrees of visual angle
                MAE = (dist[thr] * 8.0).mean().item()
        else:
            threshold = R2.view(-1) > 2.2

            loss = torch.nn.SmoothL1Loss()
            output_loss = loss(R2 * model(data), R2 * data.y.view(-1))
            output_loss.backward()

            MAE = torch.mean(abs(
                data.to(device).y.view(-1)[threshold == 1] - model(data)[
                    threshold == 1])).item()

            if grad_clip:
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            optimizer.step()
    return output_loss.detach(), MAE


def test(model, dev_loader, device, coords=False):
    model.eval()

    MeanAbsError = 0
    MeanAbsError_thr = 0
    y = []
    y_hat = []
    R2_plot = []

    for data in dev_loader:
        data = data.to(device)
        pred = model(data).detach()
        y_hat.append(pred)
        y.append(data.y if coords else data.y.view(-1))

        R2 = data.R2.view(-1)
        R2_plot.append(R2)
        threshold = R2.view(-1) > 2.2
        threshold2 = R2.view(-1) > 17

        if coords:
            mask = data.mask.view(-1)
            dist = torch.sqrt(((pred - data.y) ** 2).sum(dim=1) + 1e-12) * 8.0
            thr = (threshold) & mask
            thr2 = (threshold2) & mask
            MAE = dist[thr].mean().item()
            MAE_thr = dist[thr2].mean().item()
        else:
            MAE = torch.mean(abs(data.y.view(-1)[threshold == 1] - pred[
                threshold == 1])).item()
            MAE_thr = torch.mean(abs(
                data.y.view(-1)[threshold2 == 1] - pred[
                    threshold2 == 1])).item()
        MeanAbsError_thr += MAE_thr
        MeanAbsError += MAE

    test_MAE = MeanAbsError / len(dev_loader)
    test_MAE_thr = MeanAbsError_thr / len(dev_loader)
    output = {'Predicted_values': y_hat, 'Measured_values': y, 'R2': R2_plot,
              'MAE': test_MAE, 'MAE_thr': test_MAE_thr}
    return output

def train_loop(args):
    with open(osp.join(args.path2list)) as fp:
        subjects = fp.read().split("\n")
    if subjects[-1] == '':
        subjects = subjects[0:len(subjects) - 1]    

    norm_value = 70
    pre_transform = T.Compose([T.FaceToEdge()])

    train_dataset = Retinotopy(args.path, 'Train', transform=T.Cartesian(max_value=norm_value),
                            pre_transform=pre_transform, dataset = args.dataset, list_subs = subjects,
                            prediction=args.prediction_type, hemisphere=args.hemisphere, shuffle=True, stimulus=args.stimulus)
    dev_dataset = Retinotopy(args.path, 'Development', transform=T.Cartesian(max_value=norm_value),
                            pre_transform=pre_transform, dataset = args.dataset, list_subs = subjects,
                            prediction=args.prediction_type, hemisphere=args.hemisphere, shuffle=True, stimulus=args.stimulus)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    dev_loader = DataLoader(dev_dataset, batch_size=1, shuffle=False)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Model training
    coords = args.prediction_type == 'visualCoord'
    loss_fn = LOSSES[args.loss]

    # Per-experiment output directory + provenance. Experiment runs (visualCoord)
    # go in output/<tag>/ with a config.json (args + git SHA) and per-seed
    # trainlog.csv; the legacy single-map path keeps writing flat to output/.
    script_dir = osp.dirname(osp.realpath(__file__))
    if coords:
        tag = args.tag if args.tag else 'loss-{}_ep{}_bs{}'.format(
            args.loss, args.n_epochs, args.batch_size)
        outdir = osp.join(script_dir, 'output', tag)
    else:
        tag = ''
        outdir = osp.join(script_dir, 'output')
    if not osp.exists(outdir):
        os.makedirs(outdir)

    if coords:
        sha, dirty = _git_info(script_dir)
        config = dict(vars(args))
        config.update(tag=tag, git_sha=sha, git_dirty=dirty,
                      timestamp=datetime.datetime.now().isoformat())
        with open(osp.join(outdir, 'config_{}.json'.format(args.hemisphere)), 'w') as f:
            json.dump(config, f, indent=2)

    stim_suffix = '' if args.stimulus == 'original' else '_bars'
    use_step = (args.lr_schedule == 'step') and (not args.swa)
    swa_start = args.swa_start if args.swa_start is not None else int(0.75 * args.n_epochs)
    swa_lr = args.swa_lr if args.swa_lr is not None else args.lr * 0.1
    for i in range(args.n_seeds):
        torch.manual_seed(i)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(i)
        model = deepRetinotopy(num_features=args.num_features,
                               num_outputs=2 if coords else 1,
                               output_activation=None if coords else 'elu').to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

        cos = swalr = swa_model = None
        if args.swa:
            cos = CosineAnnealingLR(optimizer, T_max=max(1, swa_start))
            swalr = SWALR(optimizer, swa_lr=swa_lr)
            swa_model = AveragedModel(model)
        elif args.lr_schedule == 'cosine':
            cos = CosineAnnealingLR(optimizer, T_max=args.n_epochs)

        log_rows = []
        for epoch in range(1, args.n_epochs + 1):
            loss, MAE = train(epoch, model, optimizer, train_loader, device,
                              coords=coords, loss_fn=loss_fn,
                              grad_clip=args.grad_clip, step_lr=use_step)
            if args.swa and epoch >= swa_start:
                swa_model.update_parameters(model); swalr.step()
            elif cos is not None:
                cos.step()
            test_output = test(model, dev_loader, device, coords=coords)
            print(
                'Epoch: {:02d}, Train_loss: {:.4f}, Train_MAE: {:.4f}, Test_MAE: '
                '{:.4f}, Test_MAE_thr: {:.4f}'.format(
                    epoch, loss, MAE, test_output['MAE'], test_output['MAE_thr']))
            log_rows.append((epoch, float(loss), MAE,
                             test_output['MAE'], test_output['MAE_thr']))

        if args.swa:
            update_bn(train_loader, swa_model, device=device)
            swa_eval = test(swa_model, dev_loader, device, coords=coords)
            print('SWA dev MAE: {:.4f} (thr {:.4f})'.format(swa_eval['MAE'], swa_eval['MAE_thr']))
            state = swa_model.module.state_dict()
        else:
            state = model.state_dict()
        model_name = 'deepRetinotopy_{}_{}_model{}{}.pt'.format(
            args.prediction_type, args.hemisphere, i + 1, stim_suffix)
        torch.save(state, osp.join(outdir, model_name))

        if coords:
            log_name = 'trainlog_{}_model{}{}.csv'.format(
                args.hemisphere, i + 1, stim_suffix)
            with open(osp.join(outdir, log_name), 'w') as f:
                f.write('epoch,train_loss,train_mae,test_mae,test_mae_thr\n')
                for r in log_rows:
                    f.write('{},{:.6f},{:.6f},{:.6f},{:.6f}\n'.format(*r))

def main():
    parser = argparse.ArgumentParser(description='Train deepRetinotopy model')
    parser.add_argument('--path', type=str, help='Path to the data folder')
    parser.add_argument('--path2list', type=str, help='Path to the list of subjects')
    parser.add_argument('--dataset', type=str, default='HCP', help='Dataset to use')
    parser.add_argument('--prediction_type', type=str, default='polarAngle',
                        choices=['polarAngle', 'eccentricity', 'pRFsize', 'visualCoord'],
                        help='Prediction type')
    parser.add_argument('--hemisphere', type=str, default='LH',
                        choices=['LH', 'RH'], help='Hemisphere to use')
    parser.add_argument('--num_features', type=int, default=1, 
                        help='Number of features')
    parser.add_argument('--stimulus', type=str, default='original')
    parser.add_argument('--n_seeds', type=int, default=5)
    parser.add_argument('--loss', type=str, default='euclidean',
                        choices=list(LOSSES.keys()),
                        help='Loss function for visualCoord (coordinate) training')
    parser.add_argument('--n_epochs', type=int, default=200,
                        help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=1,
                        help='Training batch size (number of subjects/graphs)')
    parser.add_argument('--lr', type=float, default=0.01,
                        help='Initial Adam learning rate')
    parser.add_argument('--grad_clip', type=float, default=0.0,
                        help='Max gradient norm for clipping (0 = off)')
    parser.add_argument('--lr_schedule', type=str, default='step',
                        choices=['step', 'cosine'],
                        help="LR schedule ('step'=legacy halve@100; ignored if --swa)")
    parser.add_argument('--swa', action='store_true',
                        help='Stochastic Weight Averaging (saves one averaged model)')
    parser.add_argument('--swa_start', type=int, default=None,
                        help='Epoch to start SWA averaging (default 0.75*n_epochs)')
    parser.add_argument('--swa_lr', type=float, default=None,
                        help='Constant SWA learning rate (default lr/10)')
    parser.add_argument('--tag', type=str, default='',
                        help='Experiment tag: output subdir output/<tag>/ and '
                             'provenance. Default: loss-<loss>_ep<n_epochs>_bs<batch_size>')
    args = parser.parse_args()
    train_loop(args)


if __name__ == '__main__':
    main()

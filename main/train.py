import os
import os.path as osp
import torch
import torch_geometric.transforms as T
import sys
import time
import argparse
from torch_geometric.loader import DataLoader

sys.path.append('..')

from utils.model import deepRetinotopy
from utils.dataset import Retinotopy

def train(epoch, model, optimizer, train_loader, device, loss_type='original'):
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
        if loss_type == 'original':
            output_loss = loss(R2 * model(data), R2 * data.y.view(-1))
        elif loss_type == 'no_weight':
            output_loss = loss(model(data), data.y.view(-1))
        elif loss_type == 'logscale':
            output_loss = loss(torch.log(torch.abs(model(data))), torch.log(torch.abs(data.y.view(-1))))
        elif loss_type == 'probabilistic':
            prob = data.prob.view(-1)
            output_loss = loss(R2 * model(data) * prob, R2 * data.y.view(-1) * prob)
        output_loss.backward()

        MAE = torch.mean(abs(
            data.to(device).y.view(-1)[threshold == 1] - model(data)[
                threshold == 1])).item() 

        optimizer.step()
    return output_loss.detach(), MAE


def test(model, dev_loader, device):
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
            threshold == 1])).item()  
        MAE_thr = torch.mean(abs(
            data.to(device).y.view(-1)[threshold2 == 1] - pred[
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
    print(torch.cuda.is_available())
    print(torch.cuda.get_device_name(0))
    print('Using ' + args.dataset + ' dataset')
    print('Using ' + args.prediction_type + ' prediction')
    print('Using ' + args.hemisphere + ' hemisphere')
    
    if args.num_features == 2:
        train_dataset = Retinotopy(args.path, 'Train', transform=T.Cartesian(max_value=norm_value),
                                pre_transform=pre_transform, dataset = args.dataset, list_subs = subjects, myelination=True,
                                prediction=args.prediction_type, hemisphere=args.hemisphere, shuffle=True, stimulus=args.stimulus)
        dev_dataset = Retinotopy(args.path, 'Development', transform=T.Cartesian(max_value=norm_value),
                                pre_transform=pre_transform, dataset = args.dataset, list_subs = subjects, myelination=True,
                                prediction=args.prediction_type, hemisphere=args.hemisphere, shuffle=True, stimulus=args.stimulus)

    else:
        train_dataset = Retinotopy(args.path, 'Train', transform=T.Cartesian(max_value=norm_value),
                                pre_transform=pre_transform, dataset = args.dataset, list_subs = subjects,
                                prediction=args.prediction_type, hemisphere=args.hemisphere, shuffle=True, stimulus=args.stimulus)
        dev_dataset = Retinotopy(args.path, 'Development', transform=T.Cartesian(max_value=norm_value),
                                pre_transform=pre_transform, dataset = args.dataset, list_subs = subjects,
                                prediction=args.prediction_type, hemisphere=args.hemisphere, shuffle=True, stimulus=args.stimulus)
    print(len(train_dataset), len(dev_dataset))
    print('Stimulus: ' + args.stimulus)
    train_loader = DataLoader(train_dataset, batch_size=1, shuffle=True)
    dev_loader = DataLoader(dev_dataset, batch_size=1, shuffle=False)


    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Create an output folder if it doesn't already exist
    directory = './output'
    if not osp.exists(directory):
        os.makedirs(directory)

    # Model training
    for i in range(args.n_seeds):
        model = deepRetinotopy(num_features=args.num_features).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        for epoch in range(1, 201):
            loss, MAE = train(epoch, model, optimizer, train_loader, device, loss_type = args.loss)
            test_output = test(model, dev_loader, device)
            print(
                'Epoch: {:02d}, Train_loss: {:.4f}, Train_MAE: {:.4f}, Test_MAE: '
                '{:.4f}, Test_MAE_thr: {:.4f}'.format(
                    epoch, loss, MAE, test_output['MAE'], test_output['MAE_thr']))
        if args.stimulus=='original':
            if args.dataset != 'HCP':
                if args.loss != 'original':
                    torch.save(model.state_dict(),
                        osp.join(osp.dirname(osp.realpath(__file__)), 'output',
                                    'deepRetinotopy_' + args.prediction_type + '_' + args.hemisphere + '_model' + str(i+1) + '_' + args.dataset + '_' + args.loss + '.pt'))
                else:
                    torch.save(model.state_dict(),
                        osp.join(osp.dirname(osp.realpath(__file__)), 'output',
                                    'deepRetinotopy_' + args.prediction_type + '_' + args.hemisphere + '_model' + str(i+1) + '_' + args.dataset +'.pt'))       
            else:
                if args.num_features == 2:
                    torch.save(model.state_dict(),
                        osp.join(osp.dirname(osp.realpath(__file__)), 'output',
                                    'deepRetinotopy_' + args.prediction_type + '_' + args.hemisphere + '_model' + str(i+1) + '_myelincurv.pt'))
                    print('Saved model training with myelin maps')
                else:
                    torch.save(model.state_dict(),
                            osp.join(osp.dirname(osp.realpath(__file__)), 'output',
                                        'deepRetinotopy_' + args.prediction_type + '_' + args.hemisphere + '_model' + str(i+1) + '.pt'))
        else:
            torch.save(model.state_dict(),
                    osp.join(osp.dirname(osp.realpath(__file__)), 'output',
                                'deepRetinotopy_' + args.prediction_type + '_' + args.hemisphere + '_model' + str(i+1) + '_bars.pt'))

def main():
    parser = argparse.ArgumentParser(description='Train deepRetinotopy model')
    parser.add_argument('--path', type=str, help='Path to the data folder')
    parser.add_argument('--path2list', type=str, help='Path to the list of subjects')
    parser.add_argument('--dataset', type=str, default='HCP', help='Dataset to use')
    parser.add_argument('--prediction_type', type=str, default='polarAngle',
                        choices=['polarAngle', 'eccentricity', 'pRFsize'], 
                        help='Prediction type')
    parser.add_argument('--hemisphere', type=str, default='LH',
                        choices=['LH', 'RH'], help='Hemisphere to use')
    parser.add_argument('--num_features', type=int, default=1, 
                        help='Number of features')
    parser.add_argument('--stimulus', type=str, default='original')
    parser.add_argument('--n_seeds', type=int, default=5)
    parser.add_argument('--loss', type=str, default='original', choices = ['original', 'no_weight', 'logscale', 'probabilistic'])
    args = parser.parse_args()
    train_loop(args)


if __name__ == '__main__':
    main()

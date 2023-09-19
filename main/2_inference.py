import os
import os.path as osp
import torch
import torch.nn.functional as F
import torch_geometric.transforms as T
import sys
import nibabel as nib
import numpy as np
import argparse

sys.path.append('..')

from utils.dataset import Retinotopy
from torch_geometric.data import DataLoader
from utils.model import deepRetinotopy
from utils.rois import ROI_WangParcelsPlusFovea as roi

path = osp.join(osp.dirname(osp.realpath(__file__)), '../../Retinotopy',
                'data')
pre_transform = T.Compose([T.FaceToEdge()])
hemisphere = 'Left'  # or 'Right'


def test(model, data_loader, device):
    model.eval()
    y_hat = []
    for data in data_loader:
        pred = model(data.to(device)).detach()
        y_hat.append(pred)
    output = {'Predicted_values': y_hat}
    return output

def inference(args):
    list_subs = os.listdir(args.path)
    norm_value = 70.4237 # normalization parameter for distance between nodes
    # Load the dataset
    test_dataset = Retinotopy(args.path, 'Test',
                            transform=T.Cartesian(max_value=norm_value),
                            pre_transform=pre_transform, dataset = args.dataset,
                            list_subs=list_subs,
                            prediction=args.prediction_type, hemisphere=args.hemisphere)
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)

    for i in range(5):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = deepRetinotopy(num_features=args.num_features).to(device)
        if args.hemisphere == 'Left':
            model.load_state_dict(
                torch.load('./../models/deepRetinotopy_' + args.prediction_type + '_LH_model' + str(i + 1) + '.pt',
                    map_location=device))
        else:
            model.load_state_dict(
                torch.load('./../models/deepRetinotopy_' + args.prediction_type + '_RH_model' + str(i + 1) + '.pt',
                    map_location=device))

        # Create an output folder if it doesn't already exist
        directory = './../predictions'
        if not osp.exists(directory):
            os.makedirs(directory)

        # Run the model on the test set
        evaluation = test(model=model, data_loader=test_loader, device=device)
        torch.save({'Predicted_values': evaluation['Predicted_values']},
                osp.join(osp.dirname(osp.realpath(__file__)),
                            '../predictions/',
                            str(args.dataset) + '_curvatureFeat_' + args.prediction_type +'_model' + str(
                                i + 1) + '.pt'))

        
        # Setting the ROI
        label_primary_visual_areas = ['ROI']
        final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(
            label_primary_visual_areas)

        for j in range(len(list_subs)):
            print('Saving .gii files in: ' + args.path + '/' + list_subs[j] + '/deepRetinotopy/' )
            if not osp.exists(args.path + '/' + list_subs[j] + '/deepRetinotopy/'):
                os.makedirs(args.path + '/' + list_subs[j] + '/deepRetinotopy/')
            
            if args.hemisphere == 'Left':
                template = nib.load(args.path + '/' + list_subs[j] + '/surf/'+ list_subs[j] + '.curvature-midthickness.' + 
                                    'lh.32k_fs_LR.func.gii')
                pred = np.zeros((32492, 1))
                pred[final_mask_L == 1] = np.reshape(np.array(evaluation['Predicted_values'][j]), (-1, 1))

                # rescaling the predicted values
                minus = pred >= 180
                sum = pred < 180
                pred[minus] = pred[minus] - 180
                pred[sum] = pred[sum] + 180
                pred = np.array(pred) 

                pred[final_mask_L != 1] = -1

                template.agg_data()[:]=np.reshape(pred,(-1))

                nib.gifti.giftiio.write(template, args.path + '/' + list_subs[j] + '/deepRetinotopy/'+ list_subs[j] + '.fs_predicted_' + args.prediction_type + 
                                        '_lh_curvatureFeat_model' + str(i + 1)+ '.func.gii')
            else:
                template = nib.load(args.path + '/' + list_subs[j] + '/surf/'+ list_subs[j] + '.curvature-midthickness.' + 
                                    'rh.32k_fs_LR.func.gii')
                pred = np.zeros((32492, 1))
                pred[final_mask_R == 1] = np.reshape(np.array(evaluation['Predicted_values'][j]), (-1, 1))
                pred = np.array(pred) 

                pred[final_mask_R != 1] = -1

                template.agg_data()[:]=np.reshape(pred,(-1))

                nib.gifti.giftiio.write(template, args.path + '/' + list_subs[j] + '/deepRetinotopy/'+ list_subs[j] + '.fs_predicted_' + args.prediction_type + 
                                        '_rh_curvatureFeat_model' + str(i + 1)+ '.func.gii')

def main():
    parser = argparse.ArgumentParser(description='Deep Retinotopy')
    parser.add_argument('--path', type=str)
    parser.add_argument('--dataset', type=str, default='HCP')
    parser.add_argument('--prediction_type', type=str, default='polarAngle', choices=['polarAngle', 'eccentricity', 'pRFsize'])
    parser.add_argument('--hemisphere', type=str, default='Left', choices=['Left', 'Right'])
    parser.add_argument('--num_features', type=int, default=1)
    args = parser.parse_args() 
    inference(args)

if __name__ == '__main__':
    main()

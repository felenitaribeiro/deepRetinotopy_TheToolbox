import os
import os.path as osp
import torch
import torch_geometric.transforms as T
import sys
import nibabel as nib
import numpy as np
import argparse

sys.path.append('..')

from utils.rois import ROI_WangParcelsPlusFovea as roi
from utils.model import deepRetinotopy
from torch_geometric.data import DataLoader
from utils.dataset import Retinotopy
from utils.metrics import average_prediction

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
    norm_value = 70.4237  # normalization parameter for distance between nodes
    pre_transform = T.Compose([T.FaceToEdge()])
    # Load the dataset
    test_dataset = Retinotopy(args.path, 'Test',
                              transform=T.Cartesian(max_value=norm_value),
                              pre_transform=pre_transform, dataset=args.dataset,
                              list_subs=list_subs,
                              prediction=args.prediction_type, hemisphere=args.hemisphere)
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)
    num_of_models = 5
    num_of_cortical_nodes = 32492
    predictions = np.zeros((len(list_subs), num_of_models, num_of_cortical_nodes))
    
    for i in range(num_of_models):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = deepRetinotopy(num_features=args.num_features).to(device)
        if (args.hemisphere == 'Left' or args.hemisphere == 'LH' or args.hemisphere == 'left' or args.hemisphere == 'lh'):
            model.load_state_dict(
                torch.load('./../models/deepRetinotopy_' + args.prediction_type + '_LH_model' + str(i + 1) + '.pt',
                           map_location=device))
        else:
            model.load_state_dict(
                torch.load('./../models/deepRetinotopy_' + args.prediction_type + '_RH_model' + str(i + 1) + '.pt',
                           map_location=device))

        # Run the model on the test set
        evaluation = test(model=model, data_loader=test_loader, device=device)

        # Setting the ROI
        label_primary_visual_areas = ['ROI']
        final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(
            label_primary_visual_areas)

        for j in range(len(list_subs)):
            print('Saving .gii files in: ' + args.path +
                  list_subs[j] + '/deepRetinotopy/')
            if not osp.exists(args.path + '/' + list_subs[j] + '/deepRetinotopy/'):
                os.makedirs(args.path + '/' +
                            list_subs[j] + '/deepRetinotopy/')
            
            if (args.hemisphere == 'Left' or args.hemisphere == 'LH' or args.hemisphere == 'left' or args.hemisphere == 'lh'):
                template = nib.load(args.path + '/' + list_subs[j] + '/surf/' + list_subs[j] + '.curvature-midthickness.' +
                                    'lh.32k_fs_LR.func.gii')
                pred = np.zeros((num_of_cortical_nodes, 1))
                pred[final_mask_L == 1] = np.reshape(
                    np.array(evaluation['Predicted_values'][j]), (-1, 1))
                predictions[j, i, :] = pred[:, 0]

                # if args.prediction_type == 'polarAngle':
                    # # rescaling the predicted values
                    # minus = pred >= 180
                    # sum = pred < 180
                    # pred[minus] = pred[minus] - 180
                    # pred[sum] = pred[sum] + 180
                
                pred[final_mask_L != 1] = -1

                template.agg_data()[:] = np.reshape(pred, (-1))

                nib.save(template, args.path + '/' + list_subs[j] + '/deepRetinotopy/' + list_subs[j] + '.fs_predicted_' + args.prediction_type +
                                        '_lh_curvatureFeat_model' + str(i + 1) + '.func.gii')
            else:
                template = nib.load(args.path + '/' + list_subs[j] + '/surf/' + list_subs[j] + '.curvature-midthickness.' +
                                    'rh.32k_fs_LR.func.gii')
                pred = np.zeros((num_of_cortical_nodes, 1))
                pred[final_mask_R == 1] = np.reshape(
                    np.array(evaluation['Predicted_values'][j]), (-1, 1))
                predictions[j, i, :] = pred[:, 0]

                pred[final_mask_R != 1] = -1

                template.agg_data()[:] = np.reshape(pred, (-1))

                nib.save(template, args.path + '/' + list_subs[j] + '/deepRetinotopy/' + list_subs[j] + '.fs_predicted_' + args.prediction_type +
                                        '_rh_curvatureFeat_model' + str(i + 1) + '.func.gii')
    # Average the predictions
    average_predictions = average_prediction(predictions)
    for j in range(len(list_subs)):
        if (args.hemisphere == 'Left' or args.hemisphere == 'LH' or args.hemisphere == 'left' or args.hemisphere == 'lh'):
            template = nib.load(args.path + '/' + list_subs[j] + '/surf/' + list_subs[j] + '.curvature-midthickness.' +
                                'lh.32k_fs_LR.func.gii')
            pred = average_predictions[j, :]
            pred = np.reshape(pred, (num_of_cortical_nodes,1))

            # if args.prediction_type == 'polarAngle':
                # # rescaling the predicted values
                # minus = pred >= 180
                # sum = pred < 180
                # pred[minus] = pred[minus] - 180
                # pred[sum] = pred[sum] + 180
            
            pred[final_mask_L != 1] = -1
            template.agg_data()[:] = np.reshape(pred, (-1))

            nib.save(template, args.path + '/' + list_subs[j] + '/deepRetinotopy/' + list_subs[j] + '.fs_predicted_' + args.prediction_type +
                                    '_lh_curvatureFeat_average.func.gii')
        else:
            template = nib.load(args.path + '/' + list_subs[j] + '/surf/' + list_subs[j] + '.curvature-midthickness.' +
                                'rh.32k_fs_LR.func.gii')
            pred = average_predictions[j, :]
            pred = np.reshape(pred, (num_of_cortical_nodes,1))
            pred[final_mask_R != 1] = -1
            template.agg_data()[:] = np.reshape(pred, (-1))

            nib.save(template, args.path + '/' + list_subs[j] + '/deepRetinotopy/' + list_subs[j] + '.fs_predicted_' + args.prediction_type +
                                    '_rh_curvatureFeat_average.func.gii')            
    

def main():
    parser = argparse.ArgumentParser(description='Inference with deepRetinotopy')
    parser.add_argument('--path', type=str, help='Path to the data folder')
    parser.add_argument('--dataset', type=str, default='HCP', help='Dataset to use')
    parser.add_argument('--prediction_type', type=str, default='polarAngle',
                        choices=['polarAngle', 'eccentricity', 'pRFsize'],
                        help='Prediction type')
    parser.add_argument('--hemisphere', type=str,
                        default='lh', choices=['lh', 'rh'], help='Hemisphere to use')
    parser.add_argument('--num_features', type=int, default=1, help='Number of features')
    args = parser.parse_args()
    inference(args)


if __name__ == '__main__':
    main()

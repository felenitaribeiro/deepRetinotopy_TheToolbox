import numpy as np
import torch
import os

from Retinotopy.functions.def_ROIs_WangParcels import roi as roi2
from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi
from Retinotopy.functions.plusFovea import add_fovea
from Retinotopy.functions.error_metrics import smallest_angle


def PA_difference(model):
    """Function to determine the difference between intact new_predictions (with
    intact features) and knocked out new_predictions of polar angle values for in
    dorsal early visual cortex.

    Args: #TODO
        model (str): 'deepRetinotopy' or 'average' or 'Benson14'

    Output: #TODO
        .npz files in ./../output named:
        'ErrorPerParticipant_PA_LH_WangParcels_' + str(model) + '_1-8.npz'
        'ErrorPerParticipant_PA_LH_EarlyVisualCortex_' + str(model) +
        '_1-8.npz'
        'ErrorPerParticipant_PA_LH_dorsalV1-3_' + str(model) + '_1-8.npz'

    """
    visual_areas = ['dorsalROI']
    eccentricity_mask = np.reshape(
        np.load('./../../plots/output/MaskEccentricity_'
                'above1below8ecc_LH.npz')['list'], (-1)) #TODO

    nodes = np.load('./../../Models/nodes_earlyVisualCortex.npz')['list']

    mean_error = []
    for node in nodes:
        mean_delta = []

        intact_predictions = torch.load(
            'devset_results/devset-XXX.pt', #TODO
            map_location='cpu')
        new_predictions = torch.load(
            'devset_results/devset-node'+ str(node) +'_neighborhood10.pt',
            map_location='cpu')

        # ROI settings
        label_primary_visual_areas = ['ROI']
        final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(
            label_primary_visual_areas)
        ROI1 = np.zeros((32492, 1))
        ROI1[final_mask_L == 1] = 1

        # Visual areas
        final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi2(
            visual_areas)
        primary_visual_areas = np.zeros((32492, 1))
        primary_visual_areas[final_mask_L == 1] = 1

        # Final mask
        mask = ROI1 + primary_visual_areas
        mask = mask[ROI1 == 1]

        theta_withinsubj = []

        for i in range(len(new_predictions['Predicted_values'])):
            if i == j:
                # Loading predicted values
                # Polar angles
                if model == 'deepRetinotopy':
                    pred = np.reshape(
                        np.array(new_predictions['Predicted_values'][i]),
                        (-1, 1))
                new_pred = np.reshape(
                    np.array(intact_predictions['Predited_values'][i]),
                    (-1, 1))

                # Rescaling
                if model == 'Benson14':
                    pred = np.array(pred) * (np.pi / 180)
                else:
                    minus = pred > 180
                    sum = pred < 180
                    pred[minus] = pred[minus] - 180
                    pred[sum] = pred[sum] + 180
                    pred = np.array(pred) * (np.pi / 180)

                minus = new_pred > 180
                sum = new_pred < 180
                new_pred[minus] = new_pred[minus] - 180
                new_pred[sum] = new_pred[sum] + 180
                new_pred = np.array(new_pred) * (np.pi / 180)

                # Computing delta theta
                theta = smallest_angle(pred[eccentricity_mask],
                                       new_pred[eccentricity_mask])
                theta_withinsubj.append(
                    theta[mask[eccentricity_mask] > 1])
        mean_theta_withinsubj = np.mean(np.array(theta_withinsubj), axis=1)
        mean_delta.append(mean_theta_withinsubj)
        mean_delta = np.reshape(np.array(mean_delta), (1, -1))

        mean_error.append(np.mean(mean_delta))
    np.savez('./../output/meanErrorVSnodes_dorsalEarlyVisualCortex.npz',
             list=np.reshape(mean_error, (len(nodes), -1)))


# Create an output folder if it doesn't already exist
directory = './../output'
if not os.path.exists(directory):
    os.makedirs(directory)

PA_difference('deepRetinotopy')

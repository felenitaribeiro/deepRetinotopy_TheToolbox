import numpy as np
import torch
import os

from Retinotopy.functions.def_ROIs_DorsalEarlyVisualCortex import roi as roi2
from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi
from Retinotopy.functions.error_metrics import smallest_angle


def PA_difference(model='deepRetinotopy', number=None, feature=None):
    """Function to determine the difference between predictions (PA) generated
    with intact input features and the ones generated with occluded input
    features
    in dorsal early visual cortex.

    Args:
        model (str): By default, model = 'deepRetinotopy'
        number (int): Model number
        feature (str): Occluded features ('both' or 'reverse')

    Output:
        output (.npz): Saves a .npz file in ./output with saliency scores for
            each vertex early visual cortex

    """

    visual_areas = ['ROI']  # TODO
    eccentricity_mask = np.reshape(
        np.load('./../../plots/output/MaskEccentricity_'
                'above1below8ecc_LH.npz')['list'], (-1))  # TODO

    nodes = np.load('./../../Models/nodes_earlyVisualCortex.npz')['list']

    neighborhoods = np.arange(1, 21, 1)
    for j in neighborhoods:
        mean_error = []
        for node in nodes:
            mean_delta = []
            intact_predictions = torch.load(
                '/home/uqfribe1/Desktop/Project3/testset-results'
                '/testset_results_intactFeat/testset_results'
                '/testset-intactData_model' + str(number) + '.pt',
                map_location='cpu')
            if feature == 'reverse':
                new_predictions = torch.load(
                    '/home/uqfribe1/Desktop/Project3/testset-results'
                    '/testset_results_interpretability_' + str(
                        j) + 'neighbor_reverse/testset_results_reverse'
                             '/testset-node' + str(
                        node) + '_neighborhood' + str(
                        j) + '_reversed_model' + str(number) + '.pt',
                    map_location='cpu')
            else:
                new_predictions = torch.load(
                    '/home/uqfribe1/Desktop/Project3/testset-results'
                    '/testset_results_interpretability_' + str(
                        j) + 'neighbor/testset_results'
                             '/testset-node' + str(
                        node) + '_neighborhood' + str(
                        j) + '_model' + str(number) + '.pt',
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
                # Loading predicted values
                # Polar angles
                if model == 'deepRetinotopy':
                    pred = np.reshape(
                        np.array(new_predictions['Predicted_values'][i]),
                        (-1, 1))
                new_pred = np.reshape(
                    np.array(intact_predictions['Predicted_values'][i]),
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
        np.savez(
            './../output/meanErrorVSnodes_dorsalEarlyVisualCortex_' + str(
                j) + 'neighbor_model' + str(number) + '.npz',
            list=np.reshape(mean_error, (len(nodes), -1)))


# Create an output folder if it doesn't already exist
directory = './../output'
if not os.path.exists(directory):
    os.makedirs(directory)

for k in range(5):
    PA_difference(number=k + 1, feature='both')
    PA_difference(number=k + 1, feature='reverse')

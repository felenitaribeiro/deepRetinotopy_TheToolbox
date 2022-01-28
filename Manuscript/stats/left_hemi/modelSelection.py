import numpy as np
import matplotlib.pyplot as plt
import torch
import seaborn as sns
import pandas as pd

from Retinotopy.functions.error_metrics import smallest_angle
from Retinotopy.functions.def_ROIs_DorsalEarlyVisualCortex import roi as roi2
from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi


def modelSelection(Model):
    sns.set_style("whitegrid")
    mean_across = []
    mean_delta = []
    eccentricity_mask = np.reshape(
        np.load('./../../plots/output/MaskEccentricity_'
                'above1below8ecc_LH.npz')['list'], (-1))
    for model in range(5):
        results = torch.load(
            './../../../Models/generalizability'
            '/devset_results'
            '/devset-' + str(Model) + '_model' + str(model + 1) + '.pt',
            map_location='cpu')

        theta_withinsubj = []
        theta_acrosssubj_pred = []

        # Region of interest used for training
        ROI = ['ROI']
        final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(
            ROI)
        ROI_masked = np.zeros((32492, 1))
        ROI_masked[final_mask_L == 1] = 1

        # Dorsal V1-V3
        final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi2(['ROI'])
        dorsal_earlyVisualCortex = np.zeros((32492, 1))
        dorsal_earlyVisualCortex[final_mask_L == 1] = 1

        # Final mask (selecting dorsal V1-V3 vertices)
        mask = ROI_masked + dorsal_earlyVisualCortex
        mask = mask[ROI_masked == 1]

        # Compute angle difference
        for j in range(len(results['Predicted_values'])):
            theta_pred_across_temp = []

            for i in range(len(results['Predicted_values'])):
                # Compute angle difference between predicted and ground truth
                # within subj
                if i == j:
                    # Loading predicted values
                    pred = np.reshape(np.array(results['Predicted_values'][i]),
                                      (-1, 1))
                    measured = np.reshape(
                        np.array(results['Measured_values'][j]),
                        (-1, 1))

                    # Rescaling polar angles to match the right visual field
                    # (left hemisphere)
                    minus = pred > 180
                    sum = pred < 180
                    pred[minus] = pred[minus] - 180
                    pred[sum] = pred[sum] + 180
                    pred = np.array(pred) * (np.pi / 180)

                    minus = measured > 180
                    sum = measured < 180
                    measured[minus] = measured[minus] - 180
                    measured[sum] = measured[sum] + 180
                    measured = np.array(measured) * (np.pi / 180)

                    # Computing delta theta, angle between vector defined
                    # predicted value and empirical value same subj
                    theta = smallest_angle(pred[eccentricity_mask],
                                           measured[eccentricity_mask])
                    theta_withinsubj.append(theta[mask[eccentricity_mask] > 1])
                    # print(np.shape(pred))

                # Compute angle difference across predicted maps
                if i != j:
                    # Loading predicted values
                    pred = np.reshape(np.array(results['Predicted_values'][i]),
                                      (-1, 1))
                    pred2 = np.reshape(
                        np.array(results['Predicted_values'][j]),
                        (-1, 1))

                    # Rescaling polar angles
                    minus = pred > 180
                    sum = pred < 180
                    pred[minus] = pred[minus] - 180
                    pred[sum] = pred[sum] + 180
                    pred = np.array(pred) * (np.pi / 180)

                    minus = pred2 > 180
                    sum = pred2 < 180
                    pred2[minus] = pred2[minus] - 180
                    pred2[sum] = pred2[sum] + 180
                    pred2 = np.array(pred2) * (np.pi / 180)

                    # Difference
                    theta_pred = smallest_angle(pred[eccentricity_mask],
                                                pred2[eccentricity_mask])
                    theta_pred_across_temp.append(
                        theta_pred[mask[eccentricity_mask] > 1])

            theta_acrosssubj_pred.append(
                np.mean(theta_pred_across_temp, axis=0))

        mean_theta_withinsubj = np.mean(np.array(theta_withinsubj), axis=1)
        mean_theta_acrosssubj_pred = np.mean(np.array(theta_acrosssubj_pred),
                                             axis=1)
        mean_delta.append(mean_theta_withinsubj)
        mean_across.append(mean_theta_acrosssubj_pred)

    mean_delta = np.reshape(np.array(mean_delta), (5, -1))
    mean_across = np.reshape(np.array(mean_across), (5, -1))

    fig = plt.figure()
    data = np.concatenate([[mean_across[0], len(mean_across[0]) * ['Model 1'],
                            len(mean_across[0]) * ['Individual variability']],
                           [mean_across[1], len(mean_across[1]) * ['Model 2'],
                            len(mean_across[1]) * ['Individual variability']],
                           [mean_across[2], len(mean_across[2]) * ['Model 3'],
                            len(mean_across[2]) * ['Individual variability']],
                           [mean_across[3], len(mean_across[3]) * ['Model 4'],
                            len(mean_across[3]) * ['Individual variability']],
                           [mean_across[4], len(mean_across[4]) * ['Model 5'],
                            len(mean_across[4]) * ['Individual variability']],
                           [mean_delta[0], len(mean_across[0]) * ['Model 1'],
                            len(mean_across[0]) * [
                                'Error']],
                           [mean_delta[1], len(mean_across[1]) * ['Model 2'],
                            len(mean_across[1]) * [
                                'Error']],
                           [mean_delta[2], len(mean_across[2]) * ['Model 3'],
                            len(mean_across[2]) * [
                                'Error']],
                           [mean_delta[3], len(mean_across[3]) * ['Model 4'],
                            len(mean_across[3]) * [
                                'Error']],
                           [mean_delta[4], len(mean_across[4]) * ['Model 5'],
                            len(mean_across[4]) * [
                                'Error']]],
                          axis=1)
    df = pd.DataFrame(columns=['$\Delta$$\t\Theta$', 'Model', 'Metric'],
                      data=data.T)

    df['$\Delta$$\t\Theta$'] = df['$\Delta$$\t\Theta$'].astype(float)
    print(np.mean(df['$\Delta$$\t\Theta$'][df['Metric'] == 'Error']))
    palette = ['dimgray', 'lightgray']
    ax = sns.pointplot(y='$\Delta$$\t\Theta$', x='Model',
                       hue='Metric', data=df, palette=palette,
                       join=False, dodge=True, ci=95)
    ax.set_title('Dorsal V1/V2/V3')
    # legend = plt.legend()
    # legend.remove()
    if str(Model) == 'semiSupervised':
        plt.ylim([0, 70])
    else:
        plt.ylim([0, 30])
    # plt.savefig('ModelSelection_DorsalV123.svg')
    plt.show()


models = ['intactData', 'semiSupervised', 'ctePatch', 'cteMyelinPatch',
          'cteCurvPatch']
for model in models:
    modelSelection(model)

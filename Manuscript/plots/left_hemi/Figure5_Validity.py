import numpy as np
import matplotlib.pyplot as plt
import torch
import seaborn as sns
import pandas as pd
import scipy


from Retinotopy.functions.error_metrics import smallest_angle
from Retinotopy.functions.def_ROIs_DorsalEarlyVisualCortex import roi as roi2
from Retinotopy.functions.def_ROIs_WangParcelsPlusFovea import roi

def validity_measure(measure):
    data = pd.DataFrame(columns=['Saliency', 'Nodes', 'Neighborhood', 'Feature'])
    models = ['testset-intactData_model5.pt',
              'testset-semiSupervised_model2.pt',
              'testset-ctePatch_model4.pt',
              'testset-cteCurvPatch_model2.pt',
              'testset-cteMyelinPatch_model1.pt']

    sns.set_style("whitegrid")
    mean_across = []
    mean_delta = []
    eccentricity_mask = np.reshape(
            np.load('./../output/MaskEccentricity_'
                    'above1below8ecc_LH.npz')['list'], (-1))
    for model in models:
        results = torch.load(
            '/home/uqfribe1/Desktop/Project3/Figures/figure5/'
             + str(model), map_location='cpu')

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
                    temp = predictions = torch.load(
                        '/home/uqfribe1/Desktop/Project3'
                        '/testset-results/testset_results_intactFeat/'
                        'testset_results/testset-intactData_model5.pt',
                        map_location='cpu')
                    measured = np.reshape(np.array(temp['Measured_values'][j]),
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
                    theta = smallest_angle(pred[eccentricity_mask], measured[eccentricity_mask])
                    theta_withinsubj.append(theta[mask[eccentricity_mask]>1])
                    # print(np.shape(pred))

                # Compute angle difference across predicted maps
                if i != j:
                    # Loading predicted values
                    pred = np.reshape(np.array(results['Predicted_values'][i]),
                                      (-1, 1))
                    pred2 = np.reshape(np.array(results['Predicted_values'][j]),
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
                    theta_pred = smallest_angle(pred[eccentricity_mask], pred2[eccentricity_mask])
                    theta_pred_across_temp.append(theta_pred[mask[eccentricity_mask]>1])

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
    sns.set_style("ticks")
    if measure =='Error':
        data = np.concatenate([[mean_delta[0], len(mean_delta[0]) * ['Intact'],
                                len(mean_delta[0]) * [
                                    'Error']],
                               [mean_delta[2], len(mean_delta[2]) * ['Cte'],
                                len(mean_delta[2]) * [
                                    'Error']],
                               [mean_delta[3], len(mean_delta[3]) * ['Cte curv'],
                                len(mean_delta[3]) * [
                                    'Error']],
                               [mean_delta[4], len(mean_delta[4]) * ['Cte myelin'],
                                len(mean_delta[4]) * [
                                    'Error']],
                               [mean_delta[1], len(mean_delta[1]) * ['Semi-supervised'],
                                len(mean_delta[1]) * [
                                    'Error']],],
                              axis=1)
        palette = ['#19adaf', '#008b8d', '#00696c', '#004a4d', '#002c30']
        plt.ylim([0, 60])

    else:
        data = np.concatenate(
            [[mean_across[0], len(mean_across[0]) * ['Intact'],
              len(mean_across[0]) * [
                  'Individual variability']],
             [mean_across[2], len(mean_across[2]) * ['Cte'],
              len(mean_across[2]) * [
                  'Individual variability']],
             [mean_across[3], len(mean_across[3]) * ['Cte curv'],
              len(mean_across[3]) * [
                  'Individual variability']],
             [mean_across[4], len(mean_across[4]) * ['Cte myelin'],
              len(mean_across[4]) * [
                  'Individual variability']],
             [mean_across[1], len(mean_across[1]) * ['Semi-supervised'],
              len(mean_across[1]) * [
                  'Individual variability']], ],
            axis=1)
        palette = ['#d2dbff', '#b2bcff', '#949ee0', '#7681c0', '#5865a2']
        plt.ylim([0, 50])
    for i in range(4):
        test = scipy.stats.ttest_rel(mean_delta[0], mean_delta[i+1])
        print(test)

    df = pd.DataFrame(columns=[str(measure), 'Model', 'Metric'],
                      data=data.T)
    df[str(measure)] = df[str(measure)].astype(float)
    ax = sns.barplot(y=str(measure), x='Model', data=df, palette=palette)
    ax.set_title('Dorsal V1/V2/V3')
    sns.despine()
    plt.savefig('fig5_validity_'+ str(measure)+'.svg')
    plt.show()

validity_measure('Error')
validity_measure('Individual variability')
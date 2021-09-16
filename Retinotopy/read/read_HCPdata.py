import scipy.io
import numpy as np
import torch
import os.path as osp

from numpy.random import seed
from torch_geometric.data import Data


def read_HCP(path, Hemisphere=None, index=None, surface=None, threshold=None,
             shuffle=True, visual_mask_L=None, visual_mask_R=None,
             faces_L=None, faces_R=None, myelination=None, prediction=None):
    """Read the data files and create a data object with attributes x, y, pos,
        faces and R2.

        Args:
            path (string): Path to raw dataset
            Hemisphere (string): 'Left' or 'Right' hemisphere
            index (int): Index of the participant
            surface (string): Surface template
            threshold (float): threshold for selection of vertices in the
                ROI based on the R2 of pRF modelling
            shuffle (boolean): shuffle the participants' IDs list
            visual_mask_L (numpy array): Mask of the region of interest from
                left hemisphere (32492,)
            visual_mask_R (numpy array): Mask of the region of interest from
                right hemisphere (32492,)
            faces_L (numpy array): triangular faces from the region of
                interest (number of faces, 3) in the left hemisphere
            faces_R (numpy array): triangular faces from the region of
                interest (number of faces, 3) in the right hemisphere
            myelination (boolean): True if myelin values will be used as an
                additional feature
            prediction (string): output of the model ('polarAngle' or
                'eccentricity')

        Returns:
            data (object): object of class Data (from torch_geometric.data)
                with attributes x, y, pos, faces and R2.
        """
    # Loading the measures
    curv = scipy.io.loadmat(osp.join(path, 'cifti_curv_all.mat'))['cifti_curv']
    eccentricity = \
        scipy.io.loadmat(osp.join(path, 'cifti_eccentricity_all.mat'))[
            'cifti_eccentricity']
    polarAngle = scipy.io.loadmat(osp.join(path, 'cifti_polarAngle_all.mat'))[
        'cifti_polarAngle']
    pRFsize = scipy.io.loadmat(osp.join(path, 'cifti_pRFsize_all.mat'))[
        'cifti_pRFsize']
    R2 = scipy.io.loadmat(osp.join(path, 'cifti_R2_all.mat'))['cifti_R2']
    myelin = scipy.io.loadmat(osp.join(path, 'cifti_myelin_all.mat'))[
        'cifti_myelin']

    # Defining number of nodes
    number_cortical_nodes = int(64984)
    number_hemi_nodes = int(number_cortical_nodes / 2)

    # Loading list of subjects
    with open(osp.join(path, '..', '..', 'list_subj')) as fp:
        subjects = fp.read().split("\n")
    subjects = subjects[0:len(subjects) - 1]

    seed(1)
    if shuffle == True:
        np.random.shuffle(subjects)


    if Hemisphere == 'Right':
        # Loading connectivity of triangles
        faces = torch.tensor(faces_R.T, dtype=torch.long)  # Transforming data
        # to torch data type

        if surface == 'mid':
            # Coordinates of the Right hemisphere vertices
            pos = torch.tensor((scipy.io.loadmat(
                osp.join(path, 'mid_pos_R.mat'))['mid_pos_R'].reshape(
                (number_hemi_nodes, 3))[visual_mask_R == 1]),
                               dtype=torch.float)

        if surface == 'sphere':
            pos = torch.tensor(curv['pos'][0][0][
                               number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes, 3))[visual_mask_R == 1], dtype=torch.float)

        # Measures for the Right hemisphere
        R2_values = torch.tensor(np.reshape(
            R2['x' + subjects[index] + '_fit1_r2_msmall'][0][0][
            number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
            dtype=torch.float)
        myelin_values = torch.tensor(np.reshape(
            myelin['x' + subjects[index] + '_myelinmap'][0][0][
            number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
            dtype=torch.float)
        curvature = torch.tensor(np.reshape(
            curv['x' + subjects[index] + '_curvature'][0][0][
            number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
            dtype=torch.float)
        eccentricity_values = torch.tensor(np.reshape(
            eccentricity['x' + subjects[index] + '_fit1_eccentricity_msmall'][
                0][0][
            number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
            dtype=torch.float)
        polarAngle_values = torch.tensor(np.reshape(
            polarAngle['x' + subjects[index] + '_fit1_polarangle_msmall'][0][
                0][
            number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
            dtype=torch.float)
        pRFsize_values = torch.tensor(np.reshape(
            pRFsize['x' + subjects[index] + '_fit1_receptivefieldsize_msmall'][
                0][0][
            number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
            dtype=torch.float)

        nocurv = np.isnan(curvature)
        curvature[nocurv == 1] = 0

        nomyelin = np.isnan(myelin_values)
        myelin_values[nomyelin == 1] = 0

        noR2 = np.isnan(R2_values)
        R2_values[noR2 == 1] = 0

        # condition=R2_values < threshold
        condition2 = np.isnan(eccentricity_values)
        condition3 = np.isnan(polarAngle_values)
        condition4 = np.isnan(pRFsize_values)

        # eccentricity_values[condition == 1] = -1
        eccentricity_values[condition2 == 1] = -1

        # polarAngle_values[condition==1] = -1
        polarAngle_values[condition3 == 1] = -1

        pRFsize_values[condition4 == 1] = -1

        if myelination == False:
            if prediction == 'polarAngle':
                data = Data(x=curvature, y=polarAngle_values, pos=pos)
            elif prediction == 'eccentricity':
                data = Data(x=curvature, y=eccentricity_values, pos=pos)
            else:
                data = Data(x=curvature, y=pRFsize_values, pos=pos)
        else:
            if prediction == 'polarAngle':
                data = Data(x=torch.cat((curvature, myelin_values), 1),
                            y=polarAngle_values, pos=pos)
            elif prediction == 'eccentricity':
                data = Data(x=torch.cat((curvature, myelin_values), 1),
                            y=eccentricity_values, pos=pos)
            else:
                data = Data(x=torch.cat((curvature, myelin_values), 1),
                            y=pRFsize_values, pos=pos)

        data.face = faces
        data.R2 = R2_values

    if Hemisphere == 'Left':
        # Loading connectivity of triangles
        faces = torch.tensor(faces_L.T, dtype=torch.long)  # Transforming data
        # to torch data type

        # Coordinates of the Left hemisphere vertices
        if surface == 'mid':
            pos = torch.tensor((scipy.io.loadmat(
                osp.join(path, 'mid_pos_L.mat'))['mid_pos_L'].reshape(
                (number_hemi_nodes, 3))[visual_mask_L == 1]),
                               dtype=torch.float)

        if surface == 'sphere':
            pos = torch.tensor(curv['pos'][0][0][0:number_hemi_nodes].reshape(
                (number_hemi_nodes, 3))[visual_mask_L == 1], dtype=torch.float)

        # Measures for the Left hemisphere
        R2_values = torch.tensor(np.reshape(
            R2['x' + subjects[index] + '_fit1_r2_msmall'][0][0][
            0:number_hemi_nodes].reshape((number_hemi_nodes))[
                visual_mask_L == 1], (-1, 1)), dtype=torch.float)
        myelin_values = torch.tensor(np.reshape(
            myelin['x' + subjects[index] + '_myelinmap'][0][0][
            0:number_hemi_nodes].reshape(
                (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
            dtype=torch.float)
        curvature = torch.tensor(np.reshape(
            curv['x' + subjects[index] + '_curvature'][0][0][
            0:number_hemi_nodes].reshape(
                (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
            dtype=torch.float)
        eccentricity_values = torch.tensor(np.reshape(
            eccentricity['x' + subjects[index] + '_fit1_eccentricity_msmall'][
                0][0][0:number_hemi_nodes].reshape((number_hemi_nodes))[
                visual_mask_L == 1], (-1, 1)), dtype=torch.float)
        polarAngle_values = torch.tensor(np.reshape(
            polarAngle['x' + subjects[index] + '_fit1_polarangle_msmall'][0][
                0][0:number_hemi_nodes].reshape((number_hemi_nodes))[
                visual_mask_L == 1], (-1, 1)), dtype=torch.float)
        pRFsize_values = torch.tensor(np.reshape(
            pRFsize['x' + subjects[index] + '_fit1_receptivefieldsize_msmall'][
                0][0][0:number_hemi_nodes].reshape(
                (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
            dtype=torch.float)

        nocurv = np.isnan(curvature)
        curvature[nocurv == 1] = 0

        noR2 = np.isnan(R2_values)
        R2_values[noR2 == 1] = 0

        nomyelin = np.isnan(myelin_values)
        myelin_values[nomyelin == 1] = 0

        # condition=R2_values < threshold
        condition2 = np.isnan(eccentricity_values)
        condition3 = np.isnan(polarAngle_values)
        condition4 = np.isnan(pRFsize_values)

        # eccentricity_values[condition == 1] = -1
        eccentricity_values[condition2 == 1] = -1

        # polarAngle_values[condition==1] = -1
        polarAngle_values[condition3 == 1] = -1

        pRFsize_values[condition4 == 1] = -1

        # translating polar angle values
        sum = polarAngle_values < 180
        minus = polarAngle_values > 180
        polarAngle_values[sum] = polarAngle_values[sum] + 180
        polarAngle_values[minus] = polarAngle_values[minus] - 180

        if myelination == False:
            if prediction == 'polarAngle':
                data = Data(x=curvature, y=polarAngle_values, pos=pos)
            elif prediction == 'eccentricity':
                data = Data(x=curvature, y=eccentricity_values, pos=pos)
            else:
                data = Data(x=curvature, y=pRFsize_values, pos=pos)
        else:
            if prediction == 'polarAngle':
                data = Data(x=torch.cat((curvature, myelin_values), 1),
                            y=polarAngle_values, pos=pos)
            elif prediction == 'eccentricity':
                data = Data(x=torch.cat((curvature, myelin_values), 1),
                            y=eccentricity_values, pos=pos)
            else:
                data = Data(x=torch.cat((curvature, myelin_values), 1),
                            y=pRFsize_values, pos=pos)

        data.face = faces
        data.R2 = R2_values
    return data
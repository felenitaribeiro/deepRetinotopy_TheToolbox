import scipy.io
import numpy as np
import torch
import os.path as osp
import nibabel as nib

from numpy.random import seed
from torch_geometric.data import Data


def read_HCP(path, hemisphere=None, sub_id=None, surface=None, 
             visual_mask_L=None, visual_mask_R=None,
             faces_L=None, faces_R=None, myelination=None, prediction=None):
    """Read the data files and create a data object with attributes x, y, pos,
        faces and R2.

        Args:
            path (string): Path to raw dataset
            hemisphere (string): 'Left' or 'Right' hemisphere
            sub_id (string): ID of the participant
            surface (string): Surface template
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

    if hemisphere == 'Right':
        # Loading connectivity of triangles
        faces = torch.tensor(faces_R.T, dtype=torch.long)

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
            R2['x' + str(sub_id) + '_fit1_r2_msmall'][0][0][
                number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
            dtype=torch.float)
        myelin_values = torch.tensor(np.reshape(
            myelin['x' + str(sub_id) + '_myelinmap'][0][0][
                number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
            dtype=torch.float)
        # curvature = torch.tensor(np.reshape(
        #     curv['x' + str(sub_id) + '_curvature'][0][0][
        #         number_hemi_nodes:number_cortical_nodes].reshape(
        #         (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
        #     dtype=torch.float) # curvature provided by HCP is not the same as freesurfer
        curvature = torch.tensor(np.array(nib.load(osp.join(path, '../../freesurfer/' + sub_id + '/' + sub_id +
                                                    '.curvature-midthickness.rh.32k_fs_LR.func.gii')
                                                    ).agg_data()).reshape(number_hemi_nodes, -1)[visual_mask_R == 1], dtype=torch.float)

        eccentricity_values = torch.tensor(np.reshape(
            eccentricity['x' + str(sub_id) + '_fit1_eccentricity_msmall'][
                0][0][
                number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
            dtype=torch.float)
        polarAngle_values = torch.tensor(np.reshape(
            polarAngle['x' + str(sub_id) + '_fit1_polarangle_msmall'][0][
                0][
                number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
            dtype=torch.float)
        pRFsize_values = torch.tensor(np.reshape(
            pRFsize['x' + str(sub_id) + '_fit1_receptivefieldsize_msmall'][
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

    if hemisphere == 'Left':
        # Loading connectivity of triangles
        faces = torch.tensor(faces_L.T, dtype=torch.long)

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
            R2['x' + str(sub_id) + '_fit1_r2_msmall'][0][0][
                0:number_hemi_nodes].reshape((number_hemi_nodes))[
                visual_mask_L == 1], (-1, 1)), dtype=torch.float)
        myelin_values = torch.tensor(np.reshape(
            myelin['x' + str(sub_id) + '_myelinmap'][0][0][
                0:number_hemi_nodes].reshape(
                (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
            dtype=torch.float)
        # curvature = torch.tensor(np.reshape(
        #     curv['x' + str(sub_id) + '_curvature'][0][0][
        #         0:number_hemi_nodes].reshape(
        #         (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
        #     dtype=torch.float)
        curvature = torch.tensor(np.array(nib.load(osp.join(path, '../../freesurfer/' + sub_id + '/' + sub_id +
                                                    '.curvature-midthickness.lh.32k_fs_LR.func.gii')
                                                    ).agg_data()).reshape(number_hemi_nodes, -1)[visual_mask_L == 1], dtype=torch.float)

        eccentricity_values = torch.tensor(np.reshape(
            eccentricity['x' + str(sub_id) + '_fit1_eccentricity_msmall'][
                0][0][0:number_hemi_nodes].reshape((number_hemi_nodes))[
                visual_mask_L == 1], (-1, 1)), dtype=torch.float)
        polarAngle_values = torch.tensor(np.reshape(
            polarAngle['x' + str(sub_id) + '_fit1_polarangle_msmall'][0][
                0][0:number_hemi_nodes].reshape((number_hemi_nodes))[
                visual_mask_L == 1], (-1, 1)), dtype=torch.float)
        pRFsize_values = torch.tensor(np.reshape(
            pRFsize['x' + str(sub_id) + '_fit1_receptivefieldsize_msmall'][
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


def read_gifti(path, hemisphere=None, sub_id=None, surface='mid', 
               visual_mask_L=None, visual_mask_R=None,
               faces_L=None, faces_R=None, myelination=False, prediction=None):
    """Read the data files and create a data object with attributes x, y, pos,
        faces and R2.

        Args:
            path (string): Path to raw dataset
            hemisphere (string): 'Left' or 'Right' hemisphere
            sub_id (int): ID of the participant
            surface (string): Surface template
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

    # Defining number of nodes
    number_cortical_nodes = int(64984)
    number_hemi_nodes = int(number_cortical_nodes / 2)
    if hemisphere == 'Left':
        # Loading connectivity of triangles
        faces = torch.tensor(faces_L.T, dtype=torch.long)

        # Coordinates of the Left hemisphere vertices
        if surface == 'mid':
            pos = torch.tensor((scipy.io.loadmat(
                osp.join(osp.dirname(osp.realpath(__file__)), 'templates/mid_pos_L.mat'))['mid_pos_L'].reshape(
                (number_hemi_nodes, 3))[visual_mask_L == 1]),
                dtype=torch.float)
        
        curvature = torch.tensor(np.array(nib.load(osp.join(path,
                                 sub_id + '/surf/' + sub_id + '.curvature-midthickness.lh.32k_fs_LR.func.gii')).agg_data()).reshape(
                                 number_hemi_nodes, -1)[visual_mask_L == 1], dtype=torch.float)
        nocurv = np.isnan(curvature)
        curvature[nocurv == 1] = 0

        if myelination == False:
            if prediction == 'polarAngle':
                data = Data(x=curvature, pos=pos)
            elif prediction == 'eccentricity':
                data = Data(x=curvature, pos=pos)
            else:
                data = Data(x=curvature, pos=pos)
        data.face = faces
   
    else:
        # Loading connectivity of triangles
        faces = torch.tensor(faces_R.T, dtype=torch.long)

        if surface == 'mid':
            # Coordinates of the Right hemisphere vertices
            pos = torch.tensor((scipy.io.loadmat(
                osp.join(osp.dirname(osp.realpath(__file__)), 'templates/mid_pos_R.mat'))['mid_pos_R'].reshape(
                (number_hemi_nodes, 3))[visual_mask_R == 1]),
                dtype=torch.float)


        curvature = torch.tensor(np.array(nib.load(osp.join(path,
                                 sub_id + '/surf/' + sub_id + '.curvature-midthickness.rh.32k_fs_LR.func.gii')).agg_data()).reshape(
                                 number_hemi_nodes, -1)[visual_mask_R == 1], dtype=torch.float)
        nocurv = np.isnan(curvature)
        curvature[nocurv == 1] = 0

        if myelination == False:
            if prediction == 'polarAngle':
                data = Data(x=curvature, pos=pos)
            elif prediction == 'eccentricity':
                data = Data(x=curvature, pos=pos)
            else:
                data = Data(x=curvature, pos=pos)
        data.face = faces

    return data
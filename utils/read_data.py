import scipy.io
import numpy as np
import torch
import os.path as osp
import nibabel as nib
from torch_geometric.data import Data


def read_HCP(path, hemisphere=None, sub_id=None,
             visual_mask_L=None, visual_mask_R=None,
             faces_L=None, faces_R=None, myelination=None, prediction=None):
    """Read the data files and create a data object with attributes x, y, pos,
        faces and R2.

        Args:
            path (string): Path to raw dataset
            hemisphere (string): 'Left' or 'Right' hemisphere
            sub_id (string): ID of the participant
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
                'eccentricity' or 'pRFsize')

        Returns:
            data (object): object of class Data (from torch_geometric.data)
                with attributes x, y, pos, faces and R2.
        """
    # Loading the measures
    R2 = scipy.io.loadmat(osp.join(path, 'cifti_R2_all.mat'))['cifti_R2']
    if prediction == 'polarAngle':
        polarAngle = scipy.io.loadmat(osp.join(path, 'cifti_polarAngle_all.mat'))[
            'cifti_polarAngle']
    elif prediction == 'eccentricity':
        eccentricity = \
            scipy.io.loadmat(osp.join(path, 'cifti_eccentricity_all.mat'))[
                'cifti_eccentricity']
    elif prediction == 'pRFsize':
        pRFsize = scipy.io.loadmat(osp.join(path, 'cifti_pRFsize_all.mat'))[
            'cifti_pRFsize']
    if myelination == True:
        myelin = scipy.io.loadmat(osp.join(path, 'cifti_myelin_all.mat'))[
            'cifti_myelin']

    # Defining number of nodes
    number_cortical_nodes = int(64984)
    number_hemi_nodes = int(number_cortical_nodes / 2)

    if (hemisphere == 'Right' or hemisphere == 'RH' or hemisphere == 'right' or hemisphere == 'rh'):
        # Loading connectivity of triangles
        faces = torch.tensor(faces_R.T, dtype=torch.long)
        # 3D position of the right hemisphere vertices
        pos = torch.tensor((scipy.io.loadmat(
            osp.join(path, 'mid_pos_R.mat'))['mid_pos_R'].reshape(
            (number_hemi_nodes, 3))[visual_mask_R == 1]),
            dtype=torch.float)

        # Measures for the right hemisphere
        # Functional
        R2_values = torch.tensor(np.reshape(
            R2['x' + str(sub_id) + '_fit1_r2_msmall'][0][0][
                number_hemi_nodes:number_cortical_nodes].reshape(
                (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
            dtype=torch.float)
        if prediction == 'polarAngle':
            retinotopicMap_values = torch.tensor(np.reshape(
                polarAngle['x' + str(sub_id) + '_fit1_polarangle_msmall'][0][
                    0][
                    number_hemi_nodes:number_cortical_nodes].reshape(
                    (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
                dtype=torch.float)
        elif prediction == 'eccentricity':
            retinotopicMap_values = torch.tensor(np.reshape(
                eccentricity['x' + str(sub_id) + '_fit1_eccentricity_msmall'][
                    0][0][
                    number_hemi_nodes:number_cortical_nodes].reshape(
                    (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
                dtype=torch.float)
        elif prediction == 'pRFsize':
            retinotopicMap_values = torch.tensor(np.reshape(
                pRFsize['x' + str(sub_id) + '_fit1_receptivefieldsize_msmall'][
                    0][0][
                    number_hemi_nodes:number_cortical_nodes].reshape(
                    (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
                dtype=torch.float)
        # Anatomical
        curvature = torch.tensor(np.array(nib.load(osp.join(path, '../../freesurfer/' + sub_id + '/surf/' + sub_id +
                                                            '.curvature-midthickness.rh.32k_fs_LR.func.gii')
                                                   ).agg_data()).reshape(number_hemi_nodes, -1)[visual_mask_R == 1], dtype=torch.float)
        if myelination == True:
            myelin_values = torch.tensor(np.reshape(
                myelin['x' + str(sub_id) + '_myelinmap'][0][0][
                    number_hemi_nodes:number_cortical_nodes].reshape(
                    (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
                dtype=torch.float)
            nomyelin = np.isnan(myelin_values)
            myelin_values[nomyelin == 1] = 0

        # Removing NaN values
        nocurv = np.isnan(curvature)
        curvature[nocurv == 1] = 0

        noR2 = np.isnan(R2_values)
        R2_values[noR2 == 1] = 0

        condition = np.isnan(retinotopicMap_values)
        retinotopicMap_values[condition == 1] = -1

        if myelination == False:
            data = Data(x=curvature, y=retinotopicMap_values, pos=pos)

        else:
            data = Data(x=torch.cat((curvature, myelin_values), 1),
                        y=retinotopicMap_values, pos=pos)

        data.face = faces
        data.R2 = R2_values

    elif (hemisphere == 'Left' or hemisphere == 'LH' or hemisphere == 'left' or hemisphere == 'lh'):
        # Loading connectivity of triangles
        faces = torch.tensor(faces_L.T, dtype=torch.long)
        # 3D position of the left hemisphere vertices
        pos = torch.tensor((scipy.io.loadmat(
            osp.join(path, 'mid_pos_L.mat'))['mid_pos_L'].reshape(
            (number_hemi_nodes, 3))[visual_mask_L == 1]),
            dtype=torch.float)

        # Measures for the feft hemisphere
        # Functional
        R2_values = torch.tensor(np.reshape(
            R2['x' + str(sub_id) + '_fit1_r2_msmall'][0][0][
                0:number_hemi_nodes].reshape((number_hemi_nodes))[
                visual_mask_L == 1], (-1, 1)), dtype=torch.float)
        if prediction == 'polarAngle':
            retinotopicMap_values = torch.tensor(np.reshape(
                polarAngle['x' + str(sub_id) + '_fit1_polarangle_msmall'][0][
                    0][0:number_hemi_nodes].reshape((number_hemi_nodes))[
                    visual_mask_L == 1], (-1, 1)), dtype=torch.float)
        elif prediction == 'eccentricity':
            retinotopicMap_values = torch.tensor(np.reshape(
                eccentricity['x' + str(sub_id) + '_fit1_eccentricity_msmall'][
                    0][0][0:number_hemi_nodes].reshape((number_hemi_nodes))[
                    visual_mask_L == 1], (-1, 1)), dtype=torch.float)
        elif prediction == 'pRFsize':
            retinotopicMap_values = torch.tensor(np.reshape(
                pRFsize['x' + str(sub_id) + '_fit1_receptivefieldsize_msmall'][
                    0][0][0:number_hemi_nodes].reshape(
                    (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
                dtype=torch.float)
        # Anatomical
        curvature = torch.tensor(np.array(nib.load(osp.join(path, '../../freesurfer/' + sub_id + '/surf/' + sub_id +
                                                            '.curvature-midthickness.lh.32k_fs_LR.func.gii')
                                                   ).agg_data()).reshape(number_hemi_nodes, -1)[visual_mask_L == 1], dtype=torch.float)
        if myelination == True:
            myelin_values = torch.tensor(np.reshape(
                myelin['x' + str(sub_id) + '_myelinmap'][0][0][
                    0:number_hemi_nodes].reshape(
                    (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
                dtype=torch.float)
            nomyelin = np.isnan(myelin_values)
            myelin_values[nomyelin == 1] = 0

        # Removing NaN values
        nocurv = np.isnan(curvature)
        curvature[nocurv == 1] = 0

        noR2 = np.isnan(R2_values)
        R2_values[noR2 == 1] = 0

        condition = np.isnan(retinotopicMap_values)
        retinotopicMap_values[condition == 1] = -1

        if prediction == 'polarAngle':
            # Rescaling polar angle values
            sum_180 = retinotopicMap_values < 180
            minus_180 = retinotopicMap_values > 180
            retinotopicMap_values[sum_180] = retinotopicMap_values[sum_180] + 180
            retinotopicMap_values[minus_180] = retinotopicMap_values[minus_180] - 180

        if myelination == False:
            data = Data(x=curvature, y=retinotopicMap_values, pos=pos)
        else:
            data = Data(x=torch.cat((curvature, myelin_values), 1),
                        y=retinotopicMap_values, pos=pos)

        data.face = faces
        data.R2 = R2_values
    return data


def read_gifti(path, hemisphere=None, sub_id=None,
               visual_mask_L=None, visual_mask_R=None,
               faces_L=None, faces_R=None):
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

        Returns:
            data (object): object of class Data (from torch_geometric.data)
                with attributes x, y, pos, faces and R2.
        """

    # Defining number of nodes
    number_cortical_nodes = int(64984)
    number_hemi_nodes = int(number_cortical_nodes / 2)
    if (hemisphere == 'Left' or hemisphere == 'LH' or hemisphere == 'left' or hemisphere == 'lh'):
        # Loading connectivity of triangles
        faces = torch.tensor(faces_L.T, dtype=torch.long)

        # Coordinates of the left hemisphere vertices
        pos = torch.tensor((scipy.io.loadmat(
            osp.join(osp.dirname(osp.realpath(__file__)), 'templates/mid_pos_L.mat'))['mid_pos_L'].reshape(
            (number_hemi_nodes, 3))[visual_mask_L == 1]),
            dtype=torch.float)

        curvature = torch.tensor(np.array(nib.load(osp.join(path,
                                 sub_id + '/surf/' + sub_id + '.curvature-midthickness.lh.32k_fs_LR.func.gii')).agg_data()).reshape(
                                 number_hemi_nodes, -1)[visual_mask_L == 1], dtype=torch.float)
        nocurv = np.isnan(curvature)
        curvature[nocurv == 1] = 0

        data = Data(x=curvature, pos=pos)
        data.face = faces

    elif (hemisphere == 'Right' or hemisphere == 'RH' or hemisphere == 'right' or hemisphere == 'rh'):
        # Loading connectivity of triangles
        faces = torch.tensor(faces_R.T, dtype=torch.long)

        # Coordinates of the right hemisphere vertices
        pos = torch.tensor((scipy.io.loadmat(
            osp.join(osp.dirname(osp.realpath(__file__)), 'templates/mid_pos_R.mat'))['mid_pos_R'].reshape(
            (number_hemi_nodes, 3))[visual_mask_R == 1]),
            dtype=torch.float)

        curvature = torch.tensor(np.array(nib.load(osp.join(path,
                                 sub_id + '/surf/' + sub_id + '.curvature-midthickness.rh.32k_fs_LR.func.gii')).agg_data()).reshape(
                                 number_hemi_nodes, -1)[visual_mask_R == 1], dtype=torch.float)
        nocurv = np.isnan(curvature)
        curvature[nocurv == 1] = 0

        data = Data(x=curvature, pos=pos)
        data.face = faces

    return data

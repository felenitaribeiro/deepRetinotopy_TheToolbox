import scipy.io
import numpy as np
import torch
import os.path as osp
import nibabel as nib
from torch_geometric.data import Data

ECC_MAX = 8.0


def _coords_from_pa_ecc(pa_values, ecc_values):
    """Convert (polar angle in deg, eccentricity in deg) to normalized Cartesian
    coordinates (x, y) = ecc * (cos, sin) / ECC_MAX, with a validity mask.
    Invalid (NaN) vertices get coordinate (0, 0) and mask False. No polar-angle
    shift is applied: the Cartesian representation is smooth across the 0/360
    wrap for both hemispheres."""
    valid = ~(torch.isnan(pa_values) | torch.isnan(ecc_values))  # (N, 1)
    pa_rad = torch.deg2rad(pa_values)
    x_coord = ecc_values * torch.cos(pa_rad)
    y_coord = ecc_values * torch.sin(pa_rad)
    coords = torch.cat([x_coord, y_coord], dim=1) / ECC_MAX  # (N, 2)
    coords[~valid.view(-1)] = 0.0
    return coords.float(), valid


def read_HCP(path, hemisphere=None, sub_id=None,
             visual_mask_L=None, visual_mask_R=None,
             faces_L=None, faces_R=None, myelination=None, prediction=None, 
             stimulus = 'original'):
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
            stimulus (string): stimulus used for estimating pRF parameters from empirical data ('original' or 'bars1bars2')
        Returns:
            data (object): object of class Data (from torch_geometric.data)
                with attributes x, y, pos, faces and R2.
        """
    # Loading the measures
    R2 = scipy.io.loadmat(osp.join(path, 'cifti_R2_all.mat'))['cifti_R2']
    if prediction == 'visualCoord' and stimulus != 'original':
        raise NotImplementedError(
            "visualCoord prediction currently supports stimulus='original' only")
    if prediction in ('polarAngle', 'visualCoord'):
        polarAngle = scipy.io.loadmat(osp.join(path, 'cifti_polarAngle_all.mat'))[
            'cifti_polarAngle']
    if prediction in ('eccentricity', 'visualCoord'):
        eccentricity = \
            scipy.io.loadmat(osp.join(path, 'cifti_eccentricity_all.mat'))[
                'cifti_eccentricity']
    if prediction == 'pRFsize':
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
        if stimulus == 'original':
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
            elif prediction == 'visualCoord':
                pa_values = torch.tensor(np.reshape(
                    polarAngle['x' + str(sub_id) + '_fit1_polarangle_msmall'][0][0][
                        number_hemi_nodes:number_cortical_nodes].reshape(
                        (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
                    dtype=torch.float)
                ecc_values = torch.tensor(np.reshape(
                    eccentricity['x' + str(sub_id) + '_fit1_eccentricity_msmall'][0][0][
                        number_hemi_nodes:number_cortical_nodes].reshape(
                        (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
                    dtype=torch.float)
        else:
            R2_values = torch.tensor(np.reshape(
                nib.load(osp.join(path,'../../empirical_data_bars/' + str(sub_id) + '.fs_empirical_variance_explained_rh_masked_' + str(stimulus) + '.func.gii')).agg_data().reshape(
                    (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
                dtype=torch.float) * 100
            if prediction == 'polarAngle':
                retinotopicMap_values = torch.tensor(np.reshape(
                    nib.load(osp.join(path,'../../empirical_data_bars/' + str(sub_id) + '.fs_empirical_polarAngle_rh_masked_' + str(stimulus) + '.func.gii')).agg_data().reshape(
                    (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
                dtype=torch.float)
            elif prediction == 'eccentricity':
                retinotopicMap_values = torch.tensor(np.reshape(
                    nib.load(osp.join(path,'../../empirical_data_bars/' + str(sub_id) + '.fs_empirical_eccentricity_rh_masked_' + str(stimulus) + '.func.gii')).agg_data().reshape(
                    (number_hemi_nodes))[visual_mask_R == 1], (-1, 1)),
                dtype=torch.float)
            elif prediction == 'pRFsize':
                retinotopicMap_values = torch.tensor(np.reshape(
                    nib.load(osp.join(path,'../../empirical_data_bars/' + str(sub_id) + '.fs_empirical_pRFsize_rh_masked_' + str(stimulus) + '.func.gii')).agg_data().reshape(
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

        if prediction == 'visualCoord':
            y_values, mask_values = _coords_from_pa_ecc(pa_values, ecc_values)
        else:
            condition = np.isnan(retinotopicMap_values)
            retinotopicMap_values[condition == 1] = -1
            y_values = retinotopicMap_values
            mask_values = R2_values > 0

        if myelination == False:
            data = Data(x=curvature, y=y_values, pos=pos)

        else:
            data = Data(x=torch.cat((curvature, myelin_values), 1),
                        y=y_values, pos=pos)

        data.face = faces
        data.R2 = R2_values
        data.mask = mask_values

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
        if stimulus == 'original':
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
            elif prediction == 'visualCoord':
                pa_values = torch.tensor(np.reshape(
                    polarAngle['x' + str(sub_id) + '_fit1_polarangle_msmall'][0][0][
                        0:number_hemi_nodes].reshape(
                        (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
                    dtype=torch.float)
                ecc_values = torch.tensor(np.reshape(
                    eccentricity['x' + str(sub_id) + '_fit1_eccentricity_msmall'][0][0][
                        0:number_hemi_nodes].reshape(
                        (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
                    dtype=torch.float)
        else:
            R2_values = torch.tensor(np.reshape(
                nib.load(osp.join(path,'../../empirical_data_bars/' + str(sub_id) + '.fs_empirical_variance_explained_lh_masked_' + str(stimulus) + '.func.gii')).agg_data().reshape(
                    (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
                dtype=torch.float) * 100
            if prediction == 'polarAngle':
                retinotopicMap_values = torch.tensor(np.reshape(
                    nib.load(osp.join(path,'../../empirical_data_bars/' + str(sub_id) + '.fs_empirical_polarAngle_lh_masked_' + str(stimulus) + '.func.gii')).agg_data().reshape(
                    (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
                dtype=torch.float)
            elif prediction == 'eccentricity':
                retinotopicMap_values = torch.tensor(np.reshape(
                    nib.load(osp.join(path,'../../empirical_data_bars/' + str(sub_id) + '.fs_empirical_eccentricity_lh_masked_' + str(stimulus) + '.func.gii')).agg_data().reshape(
                    (number_hemi_nodes))[visual_mask_L == 1], (-1, 1)),
                dtype=torch.float)
            elif prediction == 'pRFsize':
                retinotopicMap_values = torch.tensor(np.reshape(
                    nib.load(osp.join(path,'../../empirical_data_bars/' + str(sub_id) + '.fs_empirical_pRFsize_lh_masked_' + str(stimulus) + '.func.gii')).agg_data().reshape(
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

        if prediction == 'visualCoord':
            y_values, mask_values = _coords_from_pa_ecc(pa_values, ecc_values)
        else:
            condition = np.isnan(retinotopicMap_values)
            retinotopicMap_values[condition == 1] = -1

            if prediction == 'polarAngle':
                # Rescaling polar angle values
                sum_180 = retinotopicMap_values < 180
                minus_180 = retinotopicMap_values > 180
                retinotopicMap_values[sum_180] = retinotopicMap_values[sum_180] + 180
                retinotopicMap_values[minus_180] = retinotopicMap_values[minus_180] - 180

            y_values = retinotopicMap_values
            mask_values = R2_values > 0

        if myelination == False:
            data = Data(x=curvature, y=y_values, pos=pos)
        else:
            data = Data(x=torch.cat((curvature, myelin_values), 1),
                        y=y_values, pos=pos)

        data.face = faces
        data.R2 = R2_values
        data.mask = mask_values
    return data


def read_HCP_gifti(path, hemisphere=None, sub_id=None,
                   visual_mask_L=None, visual_mask_R=None,
                   faces_L=None, faces_R=None, myelination=None,
                   prediction=None):
    """Read the sphere.reg-frame HCP training data from per-subject GIFTI files
        and create a data object with attributes x, y, pos, faces and R2.

        Same outputs and semantics as read_HCP (stimulus='original'), but the
        empirical maps come from the re-expressed per-subject files in
        <path>/<sub_id>/surf/ (see scripts/spherereg_targets/):
            <sub>.empirical_<map>_fit1-spherereg.<h>.32k_fs_LR.func.gii
            <sub>.myelinmap-spherereg.<h>.32k_fs_LR.func.gii
        so that targets, curvature and myelin all share the sphere.reg frame.

        Args:
            path (string): Path to the freesurfer directory (one folder per subject)
            hemisphere (string): 'Left' or 'Right' hemisphere
            sub_id (string): ID of the participant
            visual_mask_L / visual_mask_R (numpy array): ROI mask (32492,)
            faces_L / faces_R (numpy array): ROI triangular faces
            myelination (boolean): True adds myelin as a second feature
            prediction (string): 'polarAngle', 'eccentricity', 'pRFsize' or
                'visualCoord'
        Returns:
            data (object): torch_geometric Data with x, y, pos, faces, R2, mask.
        """
    number_hemi_nodes = int(32492)
    hemi_left = hemisphere in ('Left', 'LH', 'left', 'lh')
    h = 'lh' if hemi_left else 'rh'
    visual_mask = visual_mask_L if hemi_left else visual_mask_R
    faces = torch.tensor((faces_L if hemi_left else faces_R).T, dtype=torch.long)

    pos_tag = 'L' if hemi_left else 'R'
    pos = torch.tensor((scipy.io.loadmat(
        osp.join(osp.dirname(osp.realpath(__file__)),
                 'templates/mid_pos_' + pos_tag + '.mat'))['mid_pos_' + pos_tag].reshape(
        (number_hemi_nodes, 3))[visual_mask == 1]),
        dtype=torch.float)

    def load_empirical(map_name):
        f = osp.join(path, sub_id, 'surf',
                     sub_id + '.empirical_' + map_name +
                     '_fit1-spherereg.' + h + '.32k_fs_LR.func.gii')
        return torch.tensor(np.reshape(
            np.array(nib.load(f).agg_data()).reshape(
                (number_hemi_nodes))[visual_mask == 1], (-1, 1)),
            dtype=torch.float)

    R2_values = load_empirical('R2')

    # Anatomical features (same files/order as read_HCP: curvature, then myelin)
    curvature = torch.tensor(np.array(nib.load(osp.join(
        path, sub_id, 'surf',
        sub_id + '.curvature-midthickness.' + h + '.32k_fs_LR.func.gii')
    ).agg_data()).reshape(number_hemi_nodes, -1)[visual_mask == 1],
        dtype=torch.float)
    nocurv = np.isnan(curvature)
    curvature[nocurv == 1] = 0

    if myelination == True:
        myelin_values = torch.tensor(np.reshape(np.array(nib.load(osp.join(
            path, sub_id, 'surf',
            sub_id + '.myelinmap-spherereg.' + h + '.32k_fs_LR.func.gii')
        ).agg_data()).reshape((number_hemi_nodes))[visual_mask == 1], (-1, 1)),
            dtype=torch.float)
        nomyelin = np.isnan(myelin_values)
        myelin_values[nomyelin == 1] = 0

    noR2 = np.isnan(R2_values)
    R2_values[noR2 == 1] = 0

    if prediction == 'visualCoord':
        pa_values = load_empirical('polarAngle')
        ecc_values = load_empirical('eccentricity')
        y_values, mask_values = _coords_from_pa_ecc(pa_values, ecc_values)
    else:
        retinotopicMap_values = load_empirical(prediction)
        condition = np.isnan(retinotopicMap_values)
        retinotopicMap_values[condition == 1] = -1

        if prediction == 'polarAngle' and hemi_left:
            # Rescaling polar angle values (same legacy LH shift as read_HCP,
            # applied after the NaN -> -1 fill so outputs match exactly)
            sum_180 = retinotopicMap_values < 180
            minus_180 = retinotopicMap_values > 180
            retinotopicMap_values[sum_180] = retinotopicMap_values[sum_180] + 180
            retinotopicMap_values[minus_180] = retinotopicMap_values[minus_180] - 180

        y_values = retinotopicMap_values
        mask_values = R2_values > 0

    if myelination == False:
        data = Data(x=curvature, y=y_values, pos=pos)
    else:
        data = Data(x=torch.cat((curvature, myelin_values), 1),
                    y=y_values, pos=pos)
    data.face = faces
    data.R2 = R2_values
    data.mask = mask_values
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

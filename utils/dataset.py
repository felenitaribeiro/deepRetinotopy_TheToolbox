import os.path as osp
import scipy.io
import torch
import numpy as np
import sys
import os
sys.path.append('..')
from numpy.random import seed
from torch_geometric.data import InMemoryDataset
from utils.read_data import read_gifti, read_HCP
from utils.labels import labels
from utils.rois import ROI_WangParcelsPlusFovea as roi


# Generates the training, dev and test set separately
class Retinotopy(InMemoryDataset):
    url = 'https://balsa.wustl.edu/study/show/9Zkk'

    def __init__(self,
                 root,
                 set=None,
                 transform=None,
                 pre_transform=None,
                 pre_filter=None,
                 dataset=None,
                 list_subs=None,
                 myelination=False,
                 prediction=None,
                 hemisphere=None,
                 shuffle=False):
        self.root = root
        self.dataset = dataset
        self.list_subs = list_subs
        self.myelination = myelination
        self.prediction = prediction
        self.hemisphere = hemisphere
        self.shuffle = shuffle
        super(Retinotopy, self).__init__(root, transform, pre_transform,
                                         pre_filter)
        self.set = set
        if self.set == 'Train':
            path = self.processed_paths[0]
        elif self.set == 'Development':
            path = self.processed_paths[1]
        else:
            path = self.processed_paths[2]
        self.data, self.slices = torch.load(path)

    @property
    def raw_file_names(self):
        return 'S1200_7T_Retinotopy_9Zkk.zip'

    @property
    def processed_file_names(self):
        if (self.hemisphere == 'Left' or self.hemisphere == 'LH' or self.hemisphere == 'left' or self.hemisphere == 'lh'):
            if self.myelination == True:
                if self.prediction == 'eccentricity':
                    return [
                        'training_ecc_LH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'development_ecc_LH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'test_ecc_LH_myelincurv_ROI_' + str(self.dataset) + '.pt']

                elif self.prediction == 'polarAngle':
                    return [
                        'training_PA_LH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'development_PA_LH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'test_PA_LH_myelincurv_ROI_' + str(self.dataset) + '.pt']

                else:
                    return [
                        'training_pRFsize_LH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'development_pRFsize__LH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'test_pRFsize_LH_myelincurv_ROI_' + str(self.dataset) + '.pt']
            else:
                if self.prediction == 'eccentricity':
                    return ['training_ecc_LH_ROI_' + str(self.dataset) + '.pt',
                            'development_ecc_LH_ROI_' +
                            str(self.dataset) + '.pt',
                            'test_ecc_LH_ROI_' + str(self.dataset) + '.pt']

                elif self.prediction == 'polarAngle':
                    return ['training_PA_LH_ROI_' + str(self.dataset) + '.pt',
                            'development_PA_LH_ROI_' +
                            str(self.dataset) + '.pt',
                            'test_PA_LH_ROI_' + str(self.dataset) + '.pt']
                else:
                    return [
                        'training_pRFsize_LH_ROI_' + str(self.dataset) + '.pt',
                        'development_pRFsize_LH_ROI_' +
                        str(self.dataset) + '.pt',
                        'test_pRFsize_LH_ROI_' + str(self.dataset) + '.pt']

        else:
            if self.myelination == True:
                if self.prediction == 'eccentricity':
                    return [
                        'training_ecc_RH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'development_ecc_RH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'test_ecc_RH_myelincurv_ROI_' + str(self.dataset) + '.pt']

                elif self.prediction == 'polarAngle':
                    return [
                        'training_PA_RH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'development_PA_RH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'test_PA_RH_myelincurv_ROI_' + str(self.dataset) + '.pt']

                else:
                    return [
                        'training_pRFsize_RH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'development_pRFsize_RH_myelincurv_ROI_' +
                        str(self.dataset) + '.pt',
                        'test_pRFsize_RH_myelincurv_ROI_' + str(self.dataset) + '.pt']
            else:
                if self.prediction == 'eccentricity':
                    return ['training_ecc_RH_ROI_' + str(self.dataset) + '.pt',
                            'development_ecc_RH_ROI_' +
                            str(self.dataset) + '.pt',
                            'test_ecc_RH_ROI_' + str(self.dataset) + '.pt']

                elif self.prediction == 'polarAngle':
                    return ['training_PA_RH_ROI_' + str(self.dataset) + '.pt',
                            'development_PA_RH_ROI_' +
                            str(self.dataset) + '.pt',
                            'test_PA_RH_ROI_' + str(self.dataset) + '.pt']

                else:
                    return [
                        'training_pRFsize_RH_ROI_' + str(self.dataset) + '.pt',
                        'development_pRFsize_RH_ROI_' +
                        str(self.dataset) + '.pt',
                        'test_pRFsize_RH_ROI_' + str(self.dataset) + '.pt']

    # def download(self):
    #     raise RuntimeError(
    #         'Dataset not found. Please download S1200_7T_Retinotopy_9Zkk.zip '
    #         'from {} and '
    #         'move it to {} and execute SettingDataset.sh'.format(self.url,
    #                                                              self.raw_dir))

    def process(self):
        # Selecting all visual areas (Wang2015) plus V1-3 fovea
        label_primary_visual_areas = ['ROI']
        final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(
            label_primary_visual_areas)

        faces_R = labels(scipy.io.loadmat(osp.join(osp.dirname(osp.realpath(__file__)), '../utils/templates/tri_faces_R.mat'))[
            'tri_faces_R'] - 1, index_R_mask)
        faces_L = labels(scipy.io.loadmat(osp.join(osp.dirname(osp.realpath(__file__)), '../utils/templates/tri_faces_L.mat'))[
            'tri_faces_L'] - 1, index_L_mask)

        seed(1)
        if self.shuffle == True:
            np.random.shuffle(self.list_subs)

        if self.dataset == 'HCP':
            path = osp.join(self.raw_dir, 'converted')
            data_list = []

            for i in range(0, len(self.list_subs)):
                data = read_HCP(path, hemisphere=self.hemisphere, 
                                sub_id=self.list_subs[i],
                                visual_mask_L=final_mask_L,
                                visual_mask_R=final_mask_R, 
                                faces_L=faces_L,
                                faces_R=faces_R, 
                                myelination=self.myelination,
                                prediction=self.prediction)
                if self.pre_transform is not None:
                    data = self.pre_transform(data)
                data_list.append(data)
            train = data_list[0:int(161)]
            dev = data_list[int(161):int(171)]
            test = data_list[int(171):int(len(data_list))]

            torch.save(self.collate(train), self.processed_paths[0])
            torch.save(self.collate(dev), self.processed_paths[1])
            torch.save(self.collate(test), self.processed_paths[2])
        else:
            # path = osp.join(self.raw_dir)
            data_list = []

            for i in range(0, len(self.list_subs)):
                data = read_gifti(self.root, hemisphere=self.hemisphere,
                                  sub_id=self.list_subs[i],
                                  visual_mask_L=final_mask_L, 
                                  visual_mask_R=final_mask_R,
                                  faces_L=faces_L, 
                                  faces_R=faces_R,
                                  prediction=self.prediction)
                if self.pre_transform is not None:
                    data = self.pre_transform(data)
                data_list.append(data)

            test = data_list[0:len(data_list)]
            torch.save(self.collate(test), self.processed_paths[2])

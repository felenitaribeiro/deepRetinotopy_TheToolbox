import os.path as osp
import scipy.io
import torch
import numpy as np
import sys
sys.path.append(osp.dirname(osp.realpath(__file__)))
from utils.rois import ROI_WangParcelsPlusFovea as roi
from utils.labels import labels
from utils.read_data import read_gifti, read_HCP, read_nyu
from torch_geometric.data import InMemoryDataset
from numpy.random import seed

# Generates the training, dev and test set separately
class Retinotopy(InMemoryDataset):
    ""'Retinotopy dataset from HCP and GIFTI files'""

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
                 shuffle=False,
                 stimulus=None):
        self.root = root
        self.dataset = dataset
        self.list_subs = list_subs
        self.myelination = myelination
        self.prediction = prediction
        self.hemisphere = hemisphere
        self.shuffle = shuffle
        self.stimulus = stimulus
        super(Retinotopy, self).__init__(root, transform, pre_transform,
                                         pre_filter)
        self.set = set
        if self.set == 'Train':
            path = self.processed_paths[0]
        elif self.set == 'Development':
            path = self.processed_paths[1]
        else:
            path = self.processed_paths[2]
        self.data, self.slices = torch.load(path, weights_only=False)

    @property
    def raw_file_names(self):
        return 'S1200_7T_Retinotopy_9Zkk.zip'

    @property
    def processed_file_names(self):
        if self.stimulus == 'original':
            name_stimulus = ''
        else:
            name_stimulus = '_' + str(self.stimulus)

        if (self.hemisphere == 'Left' or self.hemisphere == 'LH' or
                self.hemisphere == 'left' or self.hemisphere == 'lh'):
            if self.myelination == True:
                return ['training_' + self.prediction + '_LH_myelincurv_ROI_' + str(self.dataset) + name_stimulus + '.pt',
                        'development_' + self.prediction +
                        '_LH_myelincurv_ROI_' + str(self.dataset) + name_stimulus + '.pt',
                        'test_' + self.prediction + '_LH_myelincurv_ROI_' + str(self.dataset) + name_stimulus + '.pt']

            else:
                return ['training_' + self.prediction + '_LH_ROI_' + str(self.dataset) + name_stimulus + '.pt',
                        'development_' + self.prediction +
                        '_LH_ROI_' + str(self.dataset) + name_stimulus + '.pt',
                        'test_' + self.prediction + '_LH_ROI_' + str(self.dataset) + name_stimulus + '.pt']

        else:
            if self.myelination == True:
                return ['training_' + self.prediction + '_RH_myelincurv_ROI_' + str(self.dataset) + name_stimulus + '.pt',
                        'development_' + self.prediction +
                        '_RH_myelincurv_ROI_' + str(self.dataset) + name_stimulus + '.pt',
                        'test_' + self.prediction + '_RH_myelincurv_ROI_' + str(self.dataset) + name_stimulus + '.pt']
            else:
                return ['training_' + self.prediction + '_RH_ROI_' + str(self.dataset) + name_stimulus + '.pt',
                        'development_' + self.prediction +
                        '_RH_ROI_' + str(self.dataset) + name_stimulus + '.pt',
                        'test_' + self.prediction + '_RH_ROI_' + str(self.dataset) + name_stimulus + '.pt']

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
            subs_id = []

            # Subsets from original paper
            dev_subs = ['186949', '169747', '826353', '825048', '671855',
                        '751550', '318637', '131722', '137128', '706040']
            test_subs = ['680957', '191841', '617748', '725751', '198653',
                         '191336', '572045', '601127', '644246', '157336']
            for sub in dev_subs:
                self.list_subs.remove(sub)
            for sub in test_subs:
                self.list_subs.remove(sub)

            self.list_subs = self.list_subs + dev_subs + test_subs

            for i in range(0, len(self.list_subs)):
                data = read_HCP(path, hemisphere=self.hemisphere,
                                sub_id=self.list_subs[i],
                                visual_mask_L=final_mask_L,
                                visual_mask_R=final_mask_R,
                                faces_L=faces_L,
                                faces_R=faces_R,
                                myelination=self.myelination,
                                prediction=self.prediction,
                                stimulus=self.stimulus)
                if self.pre_transform is not None:
                    data = self.pre_transform(data)
                subs_id.append(self.list_subs[i])
                data_list.append(data)

            train = data_list[0:int(161)]
            dev = data_list[int(161):int(171)]
            test = data_list[int(171):int(len(data_list))]

            assert dev_subs == subs_id[int(161):int(171)]
            assert test_subs == subs_id[int(171):int(len(data_list))]

            torch.save(self.collate(train), self.processed_paths[0])
            torch.save(self.collate(dev), self.processed_paths[1])
            torch.save(self.collate(test), self.processed_paths[2])
        elif self.dataset == 'NYU':
            path = self.raw_dir[:-4]
            data_list = []
            subs_id = []
            print(path)

            for i in range(0, len(self.list_subs)):
                data = read_nyu(path, hemisphere=self.hemisphere,
                                sub_id=self.list_subs[i],
                                visual_mask_L=final_mask_L,
                                visual_mask_R=final_mask_R,
                                faces_L=faces_L,
                                faces_R=faces_R,
                                myelination=self.myelination,
                                prediction=self.prediction,
                                stimulus=self.stimulus)
                if self.pre_transform is not None:
                    data = self.pre_transform(data)
                subs_id.append(self.list_subs[i])
                data_list.append(data)

            train = data_list[0:int(len(self.list_subs))]
            dev = data_list[0:int(len(self.list_subs))]

            torch.save(self.collate(train), self.processed_paths[0])
            torch.save(self.collate(dev), self.processed_paths[1])
        else:
            data_list = []

            for i in range(0, len(self.list_subs)):
                data = read_gifti(self.root, hemisphere=self.hemisphere,
                                  sub_id=self.list_subs[i],
                                  visual_mask_L=final_mask_L,
                                  visual_mask_R=final_mask_R,
                                  faces_L=faces_L,
                                  faces_R=faces_R,
                                  myelination=self.myelination,)
                if self.pre_transform is not None:
                    data = self.pre_transform(data)
                data_list.append(data)

            test = data_list[0:len(data_list)]
            torch.save(self.collate(test), self.processed_paths[2])

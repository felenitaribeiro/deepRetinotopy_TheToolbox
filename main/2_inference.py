#!/usr/bin/env python

import os
import os.path as osp
import torch
import torch_geometric.transforms as T
import sys
import nibabel as nib
import numpy as np
import argparse
import time
import warnings
warnings.filterwarnings("ignore")

sys.path.append(osp.dirname(osp.realpath(__file__)) + '/..')

from utils.rois import ROI_WangParcelsPlusFovea as roi
from utils.model import deepRetinotopy
from torch_geometric.data import DataLoader
from utils.dataset import Retinotopy

def test(model, data_loader, device):
    model.eval()
    y_hat = []
    for data in data_loader:
        pred = model(data.to(device)).detach()
        y_hat.append(pred)
    output = {'Predicted_values': y_hat}
    return output


def inference(args):
    print("===============================================")
    print("[Step 2] STARTING INFERENCE")
    print(f"Prediction type: {args.prediction_type}")
    print(f"Hemisphere: {args.hemisphere}")
    print(f"Dataset: {args.dataset}")
    print(f"Stimulus: {args.stimulus}")
    if args.output_dir:
        print(f"Output directory: {args.output_dir}")
    else:
        print("Output mode: In-place (within FreeSurfer directory structure)")
    print("===============================================")
    
    # Start total timing
    total_start_time = time.time()
    
    # Set the data path
    if args.output_dir is not None:
        data_path = osp.abspath(args.output_dir)
        print(f"Output directory set to: {args.output_dir}")
    else:
        data_path = osp.abspath(args.path)
        print(f"Output directory not specified, using input path: {args.path}")
    
    print(f"Data path: {data_path}")
    if args.subject_id is not None:
        print(f'Processing single subject: {args.subject_id}')
        if not osp.exists(osp.join(data_path, args.subject_id)):
            raise FileNotFoundError(f"Subject directory '{args.subject_id}' not found in {data_path}")
        else:
            list_subs = [args.subject_id]
    else:
        print('Processing all subjects in the directory')
        if not osp.exists(data_path):
            raise FileNotFoundError(f"Path {data_path} does not exist.")    
        else:
            list_subs = os.listdir(data_path)
            list_subs = [sub for sub in list_subs if sub != 'fsaverage' and not sub.startswith('.') and sub != 'processed' and not sub.endswith('.txt') and sub != 'logs']

    
    print(f"Found {len(list_subs)} subjects to process: {list_subs}")
    
    # Check if the curvature files exist
    removed_subjects = []
    valid_subjects = []
    
    for subject in list_subs:
        subject_path = osp.join(data_path, subject, 'surf')
        if not osp.exists(subject_path):
            removed_subjects.append(subject)
            print(f"Removed subject '{subject}' due to missing surf directory.")
            continue
        
        curvature_file = osp.join(subject_path, f'{subject}.curvature-midthickness.{args.hemisphere}.32k_fs_LR.func.gii')
        
        if not osp.exists(curvature_file):
            removed_subjects.append(subject)
            print(f"Removed subject '{subject}' due to missing curvature files.")
        else:
            valid_subjects.append(subject)
    
    # Save removed subjects to timestamped file (only if there are any)
    if removed_subjects:
        # Create unique filename with timestamp and process info
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        process_id = os.getpid()
        removed_file = osp.join(data_path, f'removed_subjects_{timestamp}_{process_id}.txt')
        
        try:
            with open(removed_file, 'w') as f:
                for subject in removed_subjects:
                    print(subject)
                    f.write(f"{subject}\n")
            print(f"Saved {len(removed_subjects)} removed subjects to: {removed_file}")
            print(f"Removed subjects: {removed_subjects}")
        except Exception as e:
            print(f"Warning: Could not write removed subjects file: {e}")
    
    # Update the subjects list to only include valid subjects
    list_subs = valid_subjects
    print(f"Final subject list after validation: {len(list_subs)} subjects: {list_subs}")
    
    if len(list_subs) == 0:
        print("ERROR: No valid subjects found with required curvature files!")
        return

    # Create output directory if specified
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        print(f"Created output directory: {args.output_dir}")
    
    norm_value = 70 
    pre_transform = T.Compose([T.FaceToEdge()])
    
    # Load the dataset
    print('[Step 2.1] Loading the dataset...')
    init_time = time.time()
    test_dataset = Retinotopy(data_path, 'Test',
                              transform=T.Cartesian(max_value=norm_value),
                              pre_transform=pre_transform, dataset=args.dataset,
                              list_subs=list_subs,
                              prediction=args.prediction_type, hemisphere=args.hemisphere)
    print('Dataset loaded successfully')
    end_time = time.time()
    dataset_load_time = (end_time - init_time) / 60
    print(f'Dataset loading time: {dataset_load_time:.2f} minutes')
    
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)
    num_of_models = 1
    num_of_cortical_nodes = 32492
    predictions = np.zeros((len(list_subs), num_of_models, num_of_cortical_nodes))
    
    print('[Step 2.2] Generating predictions with pre-trained models...')
    for i in range(num_of_models):
        model_start_time = time.time()
        print(f'Loading model {i + 1}/{num_of_models}...')
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f'Using device: {device}')
        
        model = deepRetinotopy(num_features=args.num_features).to(device)
        if args.stimulus == 'original':
            stimulus_name = ''
        else:
            stimulus_name = '_' + args.stimulus
        
        # Load model weights
        if (args.hemisphere == 'Left' or args.hemisphere == 'LH' or args.hemisphere == 'left' or args.hemisphere == 'lh'):
            if num_of_models != 1:
                model_path = osp.dirname(osp.realpath(__file__)) + '/../models/deepRetinotopy_' + args.prediction_type + '_LH_model' + str(i + 1) + stimulus_name + '.pt'
            else:
                model_path = osp.dirname(osp.realpath(__file__)) + '/../models/deepRetinotopy_' + args.prediction_type + '_LH_model' + stimulus_name + '.pt'
        else:
            if num_of_models != 1:
                model_path = osp.dirname(osp.realpath(__file__)) + '/../models/deepRetinotopy_' + args.prediction_type + '_RH_model' + str(i + 1) + stimulus_name + '.pt'
            else:
                model_path = osp.dirname(osp.realpath(__file__)) + '/../models/deepRetinotopy_' + args.prediction_type + '_RH_model' + stimulus_name + '.pt'
        
        print(f'Loading model from: {osp.basename(model_path)}')
        model.load_state_dict(torch.load(model_path, map_location=device))

        # Run the model on the test set
        print(f'Running inference for model {i + 1}...')
        inference_start_time = time.time()
        evaluation = test(model=model, data_loader=test_loader, device=device)
        inference_time = (time.time() - inference_start_time) / 60
        print(f'Inference completed in {inference_time:.2f} minutes')

        # Setting the ROI
        label_primary_visual_areas = ['ROI']
        final_mask_L, final_mask_R, index_L_mask, index_R_mask = roi(label_primary_visual_areas)

        print(f'Saving predictions for {len(list_subs)} subjects...')
        for j, subject in enumerate(list_subs):
            subject_start_time = time.time()
            
            # Determine output directory for this subject
            output_dir = osp.join(data_path, subject, 'deepRetinotopy')
            surf_dir = osp.join(data_path, subject, 'surf')
            
            print(f'[{subject}] Saving predictions to: {output_dir}')
            
            if not osp.exists(output_dir):
                os.makedirs(output_dir)
                print(f'[{subject}] Created output directory')
            
            if (args.hemisphere == 'Left' or args.hemisphere == 'LH' or args.hemisphere == 'left' or args.hemisphere == 'lh'):
                # Try custom output directory first, then original location
                template_path = osp.join(surf_dir, f'{subject}.curvature-midthickness.lh.32k_fs_LR.func.gii')
                if not osp.exists(template_path):
                    # Fallback to original location if not in custom output
                    template_path = osp.join(data_path, subject, 'surf', f'{subject}.curvature-midthickness.lh.32k_fs_LR.func.gii')
                
                if not osp.exists(template_path):
                    print(f'[{subject}] ERROR: Template file not found: {template_path}')
                    continue
                    
                template = nib.load(template_path)
                pred = np.zeros((num_of_cortical_nodes, 1))
                pred[final_mask_L == 1] = np.reshape(
                    np.array(evaluation['Predicted_values'][j].cpu()), (-1, 1))
                predictions[j, i, :] = pred[:, 0]
                pred[final_mask_L != 1] = -1

                template.agg_data()[:] = np.reshape(pred, (-1))
                if num_of_models != 1:
                    output_filename = f'{subject}.fs_predicted_{args.prediction_type}_lh_curvatureFeat_model{i + 1}{stimulus_name}.func.gii'
                else:
                    output_filename = f'{subject}.fs_predicted_{args.prediction_type}_lh_curvatureFeat_model{stimulus_name}.func.gii'
                
                output_path = osp.join(output_dir, output_filename)
                nib.save(template, output_path)
                
            else:
                # Try custom output directory first, then original location
                template_path = osp.join(surf_dir, f'{subject}.curvature-midthickness.rh.32k_fs_LR.func.gii')
                if not osp.exists(template_path):
                    # Fallback to original location if not in custom output
                    template_path = osp.join(data_path, subject, 'surf', f'{subject}.curvature-midthickness.rh.32k_fs_LR.func.gii')
                
                if not osp.exists(template_path):
                    print(f'[{subject}] ERROR: Template file not found: {template_path}')
                    continue
                    
                template = nib.load(template_path)
                pred = np.zeros((num_of_cortical_nodes, 1))
                pred[final_mask_R == 1] = np.reshape(
                    np.array(evaluation['Predicted_values'][j].cpu()), (-1, 1))
                predictions[j, i, :] = pred[:, 0]

                pred[final_mask_R != 1] = -1

                template.agg_data()[:] = np.reshape(pred, (-1))

                if num_of_models != 1:
                    output_filename = f'{subject}.fs_predicted_{args.prediction_type}_rh_curvatureFeat_model{i + 1}{stimulus_name}.func.gii'
                else:
                    output_filename = f'{subject}.fs_predicted_{args.prediction_type}_rh_curvatureFeat_model{stimulus_name}.func.gii'
                
                output_path = osp.join(output_dir, output_filename)
                nib.save(template, output_path)
            
            subject_time = (time.time() - subject_start_time)
            print(f'[{subject}] Completed in {subject_time:.1f}s')
                
        model_end_time = time.time()
        model_time = (model_end_time - model_start_time) / 60
        print(f'Model {i + 1} processing completed in {model_time:.2f} minutes')
    
    # Calculate and display total time
    total_end_time = time.time()
    total_execution_time = total_end_time - total_start_time
    total_minutes = int(total_execution_time // 60)
    total_seconds = int(total_execution_time % 60)
    
    print("")
    print("===============================================")
    print("[Step 2] COMPLETED!")
    print(f"Total execution time: {total_minutes}m {total_seconds}s")
    
    if args.subject_id is not None:
        print(f"Subject processed: {args.subject_id}")
    else:
        print(f"Subjects processed: {len(list_subs)}")
        if removed_subjects:
            print(f"Subjects removed due to missing files: {len(removed_subjects)}")
            print(f"Removed subjects logged in: {removed_file}")
        if len(list_subs) > 0:
            avg_time_per_subject = total_execution_time / len(list_subs)
            print(f"Average time per subject: {avg_time_per_subject:.1f}s")
    
    print(f"Prediction type: {args.prediction_type} | Hemisphere: {args.hemisphere} | Dataset: {args.dataset}")
    
    if args.output_dir:
        print(f"Output location: {args.output_dir}")
    else:
        print("Output location: In-place within FreeSurfer directory")
    print("===============================================")
    
    return          
    

def main():
    parser = argparse.ArgumentParser(description='Inference with deepRetinotopy')
    parser.add_argument('--path', type=str, help='Path to the data folder')
    parser.add_argument('--dataset', type=str, default='HCP', help='Dataset to use')
    parser.add_argument('--prediction_type', type=str, default='polarAngle',
                        choices=['polarAngle', 'eccentricity', 'pRFsize'],
                        help='Prediction type')
    parser.add_argument('--hemisphere', type=str,
                        default='lh', choices=['lh', 'rh'], help='Hemisphere to use')
    parser.add_argument('--num_features', type=int, default=1, help='Number of features')
    parser.add_argument('--stimulus', type=str, default='original')
    parser.add_argument('--subject_id', type=str, default=None,
                        help='Subject ID to process. If None, all subjects will be processed.')
    parser.add_argument('--output_dir', type=str, default=None,
                        help='Output directory for generated files. If None, files will be saved within the FreeSurfer directory structure.')
    args = parser.parse_args()
    inference(args)


if __name__ == '__main__':
    main()
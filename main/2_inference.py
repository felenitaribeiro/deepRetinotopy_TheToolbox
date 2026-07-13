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
import uuid
import shutil
import atexit
warnings.filterwarnings("ignore")

sys.path.append(osp.dirname(osp.realpath(__file__)) + '/..')

from utils.rois import get_roi
from utils.model import deepRetinotopy
from torch_geometric.data import DataLoader
from utils.dataset import Retinotopy

ECC_MAX = 8.0
# max_value for T.Cartesian: normalizes edge-vector (relative-position) components.
# Must match the value used at training (main/train.py).
NORM_VALUE = 70


def _reconstruct_coords(pred_xy):
    """Convert (N, 2) normalized Cartesian predictions back to visual-field maps.

    Returns (eccentricity deg, polar angle deg in [0, 360), x deg, y deg).
    Inverse of utils.read_data._coords_from_pa_ecc."""
    xy = np.asarray(pred_xy) * ECC_MAX
    x, y = xy[:, 0], xy[:, 1]
    ecc = np.sqrt(x ** 2 + y ** 2)
    pa = np.degrees(np.arctan2(y, x))
    pa[pa < 0] += 360.0
    return ecc, pa, x, y


def _save_coord_maps(pred_xy, final_mask, template_path, output_dir, subject,
                     hemi, stimulus_name, num_of_cortical_nodes, tag='visualCoord-model'):
    """Save the joint Cartesian-coordinate model outputs as GIFTIs: the raw
    x/y visual-field coordinates AND the reconstructed polarAngle + eccentricity
    (one forward pass -> four maps). The x/y maps are CONTINUOUS (no 0/360 wrap),
    so Step 3 should resample x and y to native space and reconstruct PA/ecc there
    (PA = atan2(y, x)); resampling the polarAngle map directly would corrupt the
    0/360 seam. The <tag> token keeps experiment variants from colliding."""
    ecc_vals, pa_vals, x_vals, y_vals = _reconstruct_coords(pred_xy)
    for map_name, vals in (('polarAngle', pa_vals), ('eccentricity', ecc_vals),
                           ('x', x_vals), ('y', y_vals)):
        template = nib.load(template_path)
        pred = np.zeros((num_of_cortical_nodes, 1))
        pred[final_mask == 1] = np.reshape(vals, (-1, 1))
        # -1 background for all maps (incl. x/y). Verified safe: Step 3 resamples
        # with -current-roi, which excludes out-of-ROI vertices from the weighted
        # average, so the -1 fill never bleeds into the reconstructed native maps.
        pred[final_mask != 1] = -1
        template.agg_data()[:] = np.reshape(pred, (-1))
        output_filename = (f'{subject}.fs_predicted_{map_name}_{hemi}'
                           f'_curvatureFeat_{tag}{stimulus_name}.func.gii')
        nib.save(template, osp.join(output_dir, output_filename))
        print(f'[{subject}] Saved {map_name} ({hemi}) [{tag}]')


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
    
    # Create unique processed directory to avoid conflicts with concurrent runs
    process_id = os.getpid()
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time() * 1000) % 100000  # Last 5 digits of timestamp
    processed_dir_name = f"processed_{process_id}_{unique_id}_{timestamp}"
    
    # Set the data path
    if args.output_dir is not None:
        data_path = osp.abspath(args.output_dir)
        processed_path = osp.join(data_path, processed_dir_name)
        print(f"Output directory set to: {args.output_dir}")
    else:
        data_path = osp.abspath(args.path)
        processed_path = osp.join(data_path, processed_dir_name)
        print(f"Output directory not specified, using input path: {args.path}")
    
    print(f"Data path: {data_path}")
    print(f"Temporary processed directory: {processed_path}")
    
    # Define cleanup function for the processed directory
    def cleanup_processed_dir():
        try:
            if osp.exists(processed_path):
                shutil.rmtree(processed_path)
                print(f"Cleaned up temporary directory: {processed_path}")
        except Exception as e:
            print(f"Warning: Could not clean up temporary directory {processed_path}: {e}")
    
    # Register the cleanup function to run at exit (fallback)
    atexit.register(cleanup_processed_dir)
    
    # Use try/finally to ensure cleanup happens regardless of how the function exits
    try:
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
                # Exclude the unique processed directories from other concurrent runs
                list_subs = [sub for sub in list_subs if sub != 'fsaverage' 
                            and not sub.startswith('.') 
                            and not sub.startswith('processed_')  # Exclude all processed directories
                            and not sub.endswith('.txt') 
                            and not sub.endswith('.log') 
                            and sub != 'logs']

        
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
            timestamp_ms = int(time.time() * 1000)  # milliseconds for uniqueness
            removed_file = osp.join(data_path, f'removed_subjects_{timestamp_ms}_{process_id}.txt')
            
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
        
        pre_transform = T.Compose([T.FaceToEdge()])
        
        # Load the dataset (this will create the processed directory)
        print('[Step 2.1] Loading the dataset...')
        init_time = time.time()
        
        # Create a temporary symlink structure to avoid modifying the dataset class significantly
        # This approach creates symlinks to the original data in our unique processed directory
        temp_data_path = processed_path
        os.makedirs(temp_data_path, exist_ok=True)
        
        # Create symlinks to subject directories
        for subject in list_subs:
            original_subject_path = osp.join(data_path, subject)
            temp_subject_path = osp.join(temp_data_path, subject)
            if not osp.exists(temp_subject_path):
                try:
                    os.symlink(original_subject_path, temp_subject_path)
                except OSError:
                    # On Windows or systems without symlink support, copy the necessary files
                    shutil.copytree(original_subject_path, temp_subject_path, symlinks=True)
        
        test_dataset = Retinotopy(temp_data_path, 'Test',
                                  transform=T.Cartesian(max_value=NORM_VALUE),
                                  pre_transform=pre_transform, dataset=args.dataset,
                                  list_subs=list_subs,
                                  prediction=args.prediction_type, hemisphere=args.hemisphere,
                                  roi_name=args.roi)
        print('Dataset loaded successfully')
        end_time = time.time()
        dataset_load_time = (end_time - init_time) / 60
        print(f'Dataset loading time: {dataset_load_time:.2f} minutes')
        
        test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)
        num_of_models = args.num_of_models
        num_of_cortical_nodes = 32492
        predictions = np.zeros((len(list_subs), num_of_models, num_of_cortical_nodes))
        
        print('[Step 2.2] Generating predictions with pre-trained models...')
        for i in range(num_of_models):
            model_start_time = time.time()
            print(f'Loading model {i + 1}/{num_of_models}...')
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f'Using device: {device}')
            
            coords = args.prediction_type == 'visualCoord'
            model = deepRetinotopy(num_features=args.num_features,
                                   num_outputs=2 if coords else 1,
                                   output_activation=None if coords else 'elu').to(device)
            if args.stimulus == 'original':
                stimulus_name = ''
            else:
                stimulus_name = '_' + args.stimulus
            
            # Resolve model weights + per-model output tag. Default source is the
            # toolbox models/ dir (override with --model_dir, e.g. an experiment
            # output dir). --num_of_models>1 loops over the per-seed files
            # model1..modelN and writes one output per seed; --model_path is an
            # explicit single-file override (only meaningful for --num_of_models 1).
            HU = 'LH' if args.hemisphere in ('Left', 'LH', 'left', 'lh') else 'RH'
            model_dir = args.model_dir if args.model_dir else osp.join(
                osp.dirname(osp.realpath(__file__)), '..', 'models')
            if args.model_path and num_of_models == 1:
                model_path = args.model_path
            else:
                seed = str(i + 1) if num_of_models != 1 else ''
                model_path = osp.join(model_dir, 'deepRetinotopy_{}_{}_model{}{}.pt'.format(
                    args.prediction_type, HU, seed, stimulus_name))
            # MODEL-name token in the output filename (= Step 3's -m value):
            # "<name>-model[<seed>]". The coords path names the model via --tag
            # (default visualCoord, overridable for variant sweeps); the single-
            # variable path names it by prediction_type (e.g. pRFsize-model).
            seed_suffix = '' if num_of_models == 1 else str(i + 1)
            out_tag = '{}-model{}'.format(args.tag, seed_suffix)
            model_token = '{}-model{}'.format(args.prediction_type, seed_suffix)
            print(f'Loading model from: {osp.basename(model_path)}')
            if not osp.exists(model_path):
                raise FileNotFoundError(
                    'Model weights not found: {}\nExpected a file named '
                    'deepRetinotopy_{}_{}_model{}{}.pt in {} . Deploy the trained '
                    'model there, or pass --model_dir / --model_path.'.format(
                        model_path, args.prediction_type, HU,
                        '' if num_of_models == 1 else '<seed>', stimulus_name,
                        model_dir))
            model.load_state_dict(torch.load(model_path, map_location=device))

            # Run the model on the test set
            print(f'Running inference for model {i + 1}...')
            inference_start_time = time.time()
            evaluation = test(model=model, data_loader=test_loader, device=device)
            inference_time = (time.time() - inference_start_time) / 60
            print(f'Inference completed in {inference_time:.2f} minutes')

            # Setting the ROI (must match the ROI the model was trained on)
            final_mask_L, final_mask_R, index_L_mask, index_R_mask = get_roi(args.roi)

            print(f'Saving predictions for {len(list_subs)} subjects...')
            for j, subject in enumerate(list_subs):
                subject_start_time = time.time()
                
                # Determine output directory for this subject (use original data_path, not temp)
                output_dir = osp.join(data_path, subject, 'deepRetinotopy')
                surf_dir = osp.join(data_path, subject, 'surf')
                
                print(f'[{subject}] Saving predictions to: {output_dir}')
                
                if not osp.exists(output_dir):
                    os.makedirs(output_dir)
                    print(f'[{subject}] Created output directory')
                
                if (args.hemisphere == 'Left' or args.hemisphere == 'LH' or args.hemisphere == 'left' or args.hemisphere == 'lh'):
                    template_path = osp.join(surf_dir, f'{subject}.curvature-midthickness.lh.32k_fs_LR.func.gii')
                    if not osp.exists(template_path):
                        print(f'[{subject}] ERROR: Template file not found: {template_path}')
                        continue
                        
                    if coords:
                        _save_coord_maps(
                            np.array(evaluation['Predicted_values'][j].cpu()),
                            final_mask_L, template_path, output_dir, subject,
                            'lh', stimulus_name, num_of_cortical_nodes, tag=out_tag)
                    else:
                        template = nib.load(template_path)
                        pred = np.zeros((num_of_cortical_nodes, 1))
                        pred[final_mask_L == 1] = np.reshape(
                            np.array(evaluation['Predicted_values'][j].cpu()), (-1, 1))
                        predictions[j, i, :] = pred[:, 0]
                        pred[final_mask_L != 1] = -1

                        template.agg_data()[:] = np.reshape(pred, (-1))
                        output_filename = f'{subject}.fs_predicted_{args.prediction_type}_lh_curvatureFeat_{model_token}{stimulus_name}.func.gii'

                        output_path = osp.join(output_dir, output_filename)
                        nib.save(template, output_path)
                    
                else:
                    template_path = osp.join(surf_dir, f'{subject}.curvature-midthickness.rh.32k_fs_LR.func.gii')
                    if not osp.exists(template_path):
                        print(f'[{subject}] ERROR: Template file not found: {template_path}')
                        continue
                        
                    if coords:
                        _save_coord_maps(
                            np.array(evaluation['Predicted_values'][j].cpu()),
                            final_mask_R, template_path, output_dir, subject,
                            'rh', stimulus_name, num_of_cortical_nodes, tag=out_tag)
                    else:
                        template = nib.load(template_path)
                        pred = np.zeros((num_of_cortical_nodes, 1))
                        pred[final_mask_R == 1] = np.reshape(
                            np.array(evaluation['Predicted_values'][j].cpu()), (-1, 1))
                        predictions[j, i, :] = pred[:, 0]

                        pred[final_mask_R != 1] = -1

                        template.agg_data()[:] = np.reshape(pred, (-1))

                        output_filename = f'{subject}.fs_predicted_{args.prediction_type}_rh_curvatureFeat_{model_token}{stimulus_name}.func.gii'

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
    
    finally:
        # Always clean up, regardless of success or failure
        cleanup_processed_dir()
    
    return          
    

def main():
    parser = argparse.ArgumentParser(description='Inference with deepRetinotopy')
    parser.add_argument('--path', type=str, help='Path to the data folder')
    parser.add_argument('--dataset', type=str, default='HCP', help='Dataset to use')
    parser.add_argument('--prediction_type', type=str, default='polarAngle',
                        choices=['polarAngle', 'eccentricity', 'pRFsize', 'visualCoord'],
                        help='Prediction type')
    parser.add_argument('--hemisphere', type=str,
                        default='lh', choices=['lh', 'rh'], help='Hemisphere to use')
    parser.add_argument('--roi', type=str, default='wholebrain',
                        help="ROI subgraph used for inference (utils.rois "
                             "registry). MUST match the ROI the model was "
                             "trained on: 'wholebrain' (default) or "
                             "'wang_fovea'.")
    parser.add_argument('--num_features', type=int, default=1, help='Number of features')
    parser.add_argument('--stimulus', type=str, default='original')
    parser.add_argument('--subject_id', type=str, default=None,
                        help='Subject ID to process. If None, all subjects will be processed.')
    parser.add_argument('--output_dir', type=str, default=None,
                        help='Output directory for generated files. If None, files will be saved within the FreeSurfer directory structure.')
    parser.add_argument('--num_of_models', type=int, default=1,
                        help='Number of seed models to run per hemisphere. >1 loops '
                             'over the per-seed files model1..modelN in the model dir '
                             'and writes one output per seed, token "<name>-model<i>" '
                             '(visualCoord: <tag>-model<i>; single-map: <type>-model<i>). '
                             'Default 1 (toolbox behavior).')
    parser.add_argument('--model_dir', type=str, default=None,
                        help='Directory holding deepRetinotopy_<type>_<H>_model[<i>].pt '
                             '(default: the toolbox models/ dir). Point at an experiment '
                             'output dir to run its seeds without deploying to models/.')
    parser.add_argument('--model_path', type=str, default=None,
                        help='Explicit path to model weights (.pt). Overrides the '
                             'default models/ lookup; use for experiment variants.')
    parser.add_argument('--tag', type=str, default='visualCoord',
                        help='Model-name stem for the visualCoord output token, '
                             'written as "<tag>-model[<seed>]" (default visualCoord '
                             '-> visualCoord-model). Override for variant sweeps, '
                             'e.g. --tag loss-mse_ep300 -> loss-mse_ep300-model.')
    args = parser.parse_args()
    inference(args)


if __name__ == '__main__':
    main()
#!/usr/bin/env python

import sys
import os
import argparse
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')

from utils.fieldSign import field_sign

def generate_signMaps(args):
    print("===============================================")
    print("[FIELD SIGN GENERATION] STARTING")
    print(f"Hemisphere: {args.hemisphere}")
    print(f"Map type: {args.map}")
    print(f"Data path: {args.path}")
    print("===============================================")
    
    # Start total timing
    total_start_time = time.time()
    
    if args.subject_id is not None:
        print(f'Processing single subject: {args.subject_id}')
        if not os.path.exists(os.path.join(args.path, args.subject_id)):
            raise FileNotFoundError(f"Subject directory '{args.subject_id}' not found in {args.path}")
        else:
            list_subs = [args.subject_id]
    else:
        print('Processing all subjects in the directory')
        if not os.path.exists(args.path):
            raise FileNotFoundError(f"Path {args.path} does not exist.")
        else:
            list_subs = os.listdir(args.path)
            list_subs = [sub for sub in list_subs if sub != 'fsaverage' 
                         and not sub.startswith('.') 
                         and not sub.startswith('processed_') 
                         and not sub.endswith('.txt') 
                         and not sub.endswith('.log') 
                         and sub != 'logs']
    
    print(f"Found {len(list_subs)} subjects to process: {list_subs}")
    
    successful_subjects = 0
    failed_subjects = 0
    
    for sub in list_subs:
        subject_start_time = time.time()
        print(f"=== Processing field sign for subject: {sub} ===")
        
        path = os.path.join(args.path, sub, 'deepRetinotopy/')
        
        # Check if required files exist
        polar_angle_file = sub + '.' + args.map + '_polarAngle_' + args.hemisphere + '_curvatureFeat_model.func.gii'
        eccentricity_file = sub + '.' + args.map + '_eccentricity_' + args.hemisphere + '_curvatureFeat_model.func.gii'
        
        polar_angle_path = os.path.join(path, polar_angle_file)
        eccentricity_path = os.path.join(path, eccentricity_file)
        
        print(f"[{sub}] Looking for files in: {path}")
        print(f"[{sub}] Polar angle file: {polar_angle_file}")
        print(f"[{sub}] Eccentricity file: {eccentricity_file}")
        
        if os.path.exists(polar_angle_path) and os.path.exists(eccentricity_path):
            try:
                print(f"[{sub}] Generating field sign map...")
                field_sign(path, args.hemisphere, polar_angle_file, eccentricity_file)
                
                subject_time = time.time() - subject_start_time
                print(f"[{sub}] Field sign generation completed in {subject_time:.1f}s")
                successful_subjects += 1
                
            except Exception as e:
                print(f"[{sub}] ERROR: Field sign generation failed: {str(e)}")
                failed_subjects += 1
        else:
            missing_files = []
            if not os.path.exists(polar_angle_path):
                missing_files.append("polar angle")
            if not os.path.exists(eccentricity_path):
                missing_files.append("eccentricity")
            
            print(f"[{sub}] ERROR: Missing {' and '.join(missing_files)} map(s)")
            failed_subjects += 1
    
    # Calculate and display total time
    total_end_time = time.time()
    total_execution_time = total_end_time - total_start_time
    total_minutes = int(total_execution_time // 60)
    total_seconds = int(total_execution_time % 60)
    
    print("")
    print("===============================================")
    print("[FIELD SIGN GENERATION] COMPLETED!")
    print(f"Total execution time: {total_minutes}m {total_seconds}s")
    
    if args.subject_id is not None:
        print(f"Subject processed: {args.subject_id}")
    else:
        print(f"Subjects processed: {len(list_subs)}")
        if len(list_subs) > 0:
            avg_time_per_subject = total_execution_time / len(list_subs)
            print(f"Average time per subject: {avg_time_per_subject:.1f}s")
    
    print(f"Successful: {successful_subjects} | Failed: {failed_subjects}")
    print(f"Map type: {args.map} | Hemisphere: {args.hemisphere}")
    print("===============================================")

def main():
    parser = argparse.ArgumentParser(description='Generate field sign maps from polar angle and eccentricity maps')
    parser.add_argument('--path', type=str, help='Path to the directory containing deepRetinotopy results (FreeSurfer or specified output directory)')
    parser.add_argument('--hemisphere', type=str,
                        default='lh', choices=['lh', 'rh'], help='Hemisphere to use')
    parser.add_argument('--map', type=str, default='fs_predicted', help='Map type to use')
    parser.add_argument('--subject_id', type=str, default=None,
                        help='Subject ID to process. If None, all subjects will be processed.')
    args = parser.parse_args()
    
    generate_signMaps(args)

if __name__ == '__main__':
    main()

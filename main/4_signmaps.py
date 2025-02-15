#!/usr/bin/env python

import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')

from utils.fieldSign import field_sign

def generate_signMaps(args):
    list_subs = os.listdir(args.path)
    list_subs = [sub for sub in list_subs if sub != 'fsaverage' and not sub.startswith('.')]
    for sub in list_subs:
        path = os.path.join(args.path, sub, 'deepRetinotopy/')
        if os.path.exists(os.path.join(path, sub + '.' + args.map + '_polarAngle_' + args.hemisphere + '_curvatureFeat_model.func.gii')) and \
            os.path.exists(os.path.join(path, sub + '.' + args.map + '_eccentricity_' + args.hemisphere + '_curvatureFeat_model.func.gii')):
            field_sign(path, args.hemisphere, 
                    sub + '.' + args.map + '_polarAngle_' + args.hemisphere + '_curvatureFeat_model.func.gii',
                    sub + '.' + args.map + '_eccentricity_' + args.hemisphere + '_curvatureFeat_model.func.gii')
        else: 
            print(f'{sub} is missing either the polar angle and/or the eccentricity maps')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help='Path to the FreeSurfer directory')
    parser.add_argument('--hemisphere',type=str,
                        default='lh', choices=['lh', 'rh'], help='Hemisphere to use')
    parser.add_argument('--map', type=str, default='fs_predicted', help='Map to use')
    args = parser.parse_args()

    generate_signMaps(args)

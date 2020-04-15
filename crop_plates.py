#!/usr/bin/python

import os
import sys
import json
import math
import cv2
import numpy as np
import copy
import yaml
from argparse import ArgumentParser


parser = ArgumentParser(description='OpenALPR License Plate Cropper')

parser.add_argument( "--input_dir", dest="input_dir", action="store", type=str, required=True, 
                  help="Directory containing plate images and yaml metadata" )

parser.add_argument( "--out_dir", dest="out_dir", action="store", type=str, required=True, 
                  help="Directory to output cropped plates" )

parser.add_argument( "--zoom_out_percent", dest="zoom_out_percent", action="store", type=float, default=1.25, 
                  help="Percent multiplier to zoom out before cropping" )


options = parser.parse_args()


if not os.path.isdir(options.input_dir):
    print("input_dir (%s) doesn't exist")
    sys.exit(1)


if not os.path.isdir(options.out_dir):
    os.makedirs(options.out_dir)



count = 1
yaml_files = []
for in_file in os.listdir(options.input_dir):
    if in_file.endswith('.yaml') or in_file.endswith('.yml'):
        yaml_files.append(in_file)


yaml_files.sort()

for yaml_file in yaml_files:


    print("Processing: " + yaml_file + " (" + str(count) + "/" + str(len(yaml_files)) + ")")
    count += 1


    yaml_path = os.path.join(options.input_dir, yaml_file)
    yaml_without_ext = os.path.splitext(yaml_path)[0]
    with open(yaml_path, 'r') as yf:
        yaml_obj = yaml.load(yf)

    image = yaml_obj['image_file']

    # Skip missing images
    full_image_path = os.path.join(options.input_dir, image)
    if not os.path.isfile(full_image_path):
        print("Could not find image file %s, skipping" % (full_image_path))
        continue


    plate_corners = yaml_obj['plate_corners_gt']
    cc = plate_corners.strip().split()
    for i in range(0, len(cc)):
        cc[i] = int(cc[i])

    img = cv2.imread(full_image_path)
    mask = np.zeros(img.shape[0:2], dtype=np.uint8)
    points = np.array([[[cc[0],cc[1]],[cc[2], cc[3]], [cc[4],cc[5]], [cc[6],cc[7]]]])

    cv2.drawContours(mask, [points], -1, (255,255,255), -1, cv2.LINE_AA)

    res = cv2.bitwise_and(img,img,mask = mask)
    rect = cv2.boundingRect(points) # returns (x,y,w,h) of the rect
    cropped = res[rect[1]: rect[1] + rect[3], rect[0]: rect[0] + rect[2]]
    out_crop_path = os.path.join(options.out_dir, os.path.basename(yaml_without_ext) + ".jpg")
    cv2.imwrite(out_crop_path, cropped )


print("%d Cropped images are located in %s" % (count-1, options.out_dir))

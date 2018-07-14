from os import listdir, makedirs
from os.path import isfile, join, exists

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input_dir", help="Data input directory")
parser.add_argument("output_dir", help="Data output directory")
args = parser.parse_args()

import numpy as np
from scipy import misc
from PIL import Image

scale = 2.0
label_size = 200
patch_size = int(label_size/scale)
stride = 200

if not exists(args.output_dir):
    makedirs(args.output_dir)
if not exists(join(args.output_dir, "input")):
    makedirs(join(args.output_dir, "input"))
if not exists(join(args.output_dir, "label")):
    makedirs(join(args.output_dir, "label"))

count = 1
for f in listdir(args.input_dir):
    f = join(args.input_dir, f)
    if not isfile(f):
        continue

    image = np.asarray(Image.open(f).convert('RGB'))
    print(f, image.shape)

    h, w, c = image.shape

    scaled = misc.imresize(image, 1.0/scale, 'bicubic')

    for y in range(0, h - label_size + 1, stride):
        for x in range(0, w - label_size + 1, stride):
            (x_p, y_p) = (int(x/scale), int(y/scale))
            print(y,x,y_p,x_p)
            sub_img_patch = scaled[y_p : y_p + patch_size, x_p : x_p + patch_size]
            sub_img_label = image[y : y + label_size, x : x + label_size]
            misc.imsave(join(args.output_dir, "input", str(count) + '.png'), sub_img_patch)
            misc.imsave(join(args.output_dir, "label", str(count) + '.png'), sub_img_label)

            count += 1
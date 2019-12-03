"""
Generates jpg patches from .czi format whole slide images.
Run python patch_generator.py --help to see possible arguments.

Script by Jessica Cooper (jmc31@st-andrews.ac.uk)
"""

from czifile import CziFile
import javabridge
import bioformats
import pandas as pd
from os import listdir
import numpy as np
from PIL import Image
import argparse
import atexit


def exit_handler():
    print('Exiting...')
    javabridge.kill_vm()


atexit.register(exit_handler)

javabridge.start_vm(class_path=bioformats.JARS)

parser = argparse.ArgumentParser()
parser.add_argument('--patch_dim', type=int, default=512, help='Patch dimension. Default is 512.)')
parser.add_argument('--series', type=int, default=2, help='Czi series/zoom level. Lower number = higher resolution. Typically runs from 1 to ~7. Lower numbers may cause memory issues. Default is 2.)')
parser.add_argument('--czi_dir', default='imgs/czis', help='Location of czi files. Default is "imgs/czis"')
parser.add_argument('--patch_dir', default='imgs/patches', help='Where to save generated patches. Default is "imgs/patches"')
parser.add_argument('--jpg_dir', default='imgs/jpgs', help='Where to save entire slide jpgs. Default is "imgs/jpgs"')
parser.add_argument('--save_blank', action='store_true', help='Whether or not to save blank patches (i.e. no pixel variation whatsoever, such as at edge of slides)')
parser.add_argument('--no_patch', action='store_true', help='If you just want a jpg of the czi file without patches, use this. I suggest you set the series value high to avoid creating a giant '
                                                            'monster jpg.')

args = parser.parse_args()

PATCH_DIM = args.patch_dim
SERIES = args.series
im_names = listdir(args.czi_dir)


def normalise(x):
    return (x - x.min()) / (x.max() - x.min())


for i in im_names:

    print(i)
    img = normalise(bioformats.load_image('{}/{}'.format(args.czi_dir, i), series=SERIES)) * 255
    x_dim, y_dim = img.shape[0], img.shape[1]

    if not args.no_patch:
        for x in range(0, x_dim - PATCH_DIM, PATCH_DIM):
            for y in range(0, y_dim - PATCH_DIM, PATCH_DIM):
                print(x, y)
                patch = img[x:x + PATCH_DIM, y:y + PATCH_DIM]
                if (patch.max() - patch.min() > 0) or args.save_blank:
                    patch = Image.fromarray(patch.astype('uint8'))
                    patch.save('{}/{}_{}_{}_{}.jpg'.format(args.patch_dir, i, SERIES, x, y))

    whole_img = Image.fromarray(img.astype('uint8'))
    whole_img.save('{}/{}_{}.jpg'.format(args.jpg_dir, i, SERIES))

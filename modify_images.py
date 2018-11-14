from __future__ import print_function
import os
import numpy as np
from PIL import Image
from io import BytesIO


def rescale_g_channel():
  root = './dataset'
  for dataset in os.listdir(root):
    dataset_dir = dataset
    for category in os.listdir(os.path.join(root, dataset_dir)):


  img = Image.open(filename)
  _, g, _ = img.split()
  g = g.resize((128, 128))
  g_arr = np.array(g)
  g = np.zeros((256, 256))
  g[0:128, 0:128] = g_arr

  final = np.array(img)
  final[:, :, 1] = g
  img = Image.fromarray(final)

  img.save(dest)

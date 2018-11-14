from __future__ import print_function
import os
import csv
import numpy as np
import urllib3
import progressbar
from multiprocessing.dummy import Pool as ThreadPool
from PIL import Image
from io import BytesIO

urllib3.disable_warnings()

# make a horizontal flip on green channel and a vertical flip on the blue channel
def modify_image(image):
  img_arr = np.array(image)

  # horizontal flip on the green channel (channel 1)
  img_arr[:, :, 1] = np.flipud(img_arr[:, :, 1])

  # vertical flip on the blue channel (channel 2)
  img_arr[:, :, 2] = np.fliplr(img_arr[:, :, 2])

  return Image.fromarray(img_arr)

def download_image(url, filename, force=False):
  directory = '/'.join(filename.split('/')[:-1])

  modified_file = filename.split('/')
  modified_file[2] = modified_file[2] + '_modified'

  modified_dir = modified_file[:-1]
  modified_dir = '/'.join(modified_dir)
  modified_file = '/'.join(modified_file)

  if not os.path.exists(directory):
    os.makedirs(directory, exist_ok=True)
  if not os.path.exists(modified_dir):
    os.makedirs(modified_dir, exist_ok=True)
  if (force or not os.path.exists(filename) or not os.path.exists(modified_file)) and url != '':
    try:
      connection_pool = urllib3.PoolManager()
      resp = connection_pool.request('GET',url )

      img = Image.open(BytesIO(resp.data))
      img = img.resize((256, 256))
      img_modified = modify_image(img)

      img.save(filename)
      img_modified.save(modified_file)
      resp.release_conn()
    except:
      try:
        os.remove(filename)
        os.remove(modified_file)
      except:
        pass

widgets=[
    progressbar.BouncingBar(),
    ' ', progressbar.Counter(), ' ',
    ' [', progressbar.Timer(), '] '
]

data_root = './dataset'
csv_dir = os.path.join(data_root, 'csv_files')
for directory in os.listdir(csv_dir):
  print (directory)
  files = os.listdir(os.path.join(csv_dir, directory))
  files.sort()

  actual_dir  = os.path.join(data_root, directory)
  dog_dir     = os.path.join(actual_dir, 'dog')
  cat_dir     = os.path.join(actual_dir, 'cat')

  if not os.path.exists(dog_dir):
    os.makedirs(dog_dir, exist_ok=True)
  if not os.path.exists(cat_dir):
    os.makedirs(cat_dir, exist_ok=True)

  # Getting all ids
  ids = {}
  with open(os.path.join(csv_dir, directory, files[0])) as image_labels:
    reader = csv.DictReader(image_labels)
    for row in progressbar.progressbar(reader, widgets=widgets):
      if (row['Confidence'] == '1'):
        if (row['LabelName'] == '/m/0bt9lr'):
          ids[row['ImageID']] = 1
        elif (row['LabelName'] == '/m/01yrx'):
          ids[row['ImageID']] = 0
  print('Got all ids')
  dogs_len = len([x for x in ids.values() if x == 1])
  print(dogs_len)
  print(len([x for x in ids.values() if x == 0]))
  # Getting all urls
  urls = {}
  count_cats = 0
  count_dogs = 0
  with open(os.path.join(csv_dir, directory, files[1])) as image_ids:
    reader = csv.DictReader(image_ids)
    for row in progressbar.progressbar(reader, widgets=widgets):
      if row['ImageID'] in ids:
        if ids[row['ImageID']] == 1:
          if (count_dogs < 20000):
            urls[os.path.join(dog_dir, row['Thumbnail300KURL'].split('/')[-1])] = row['Thumbnail300KURL']
            count_dogs += 1
        elif ids[row['ImageID']] == 0:
          if(count_cats < 20000):
            urls[os.path.join(cat_dir, row['Thumbnail300KURL'].split('/')[-1])] = row['Thumbnail300KURL']
            count_cats += 1
    print('Got all urls')
    print(len(urls))

  # Downloading images
  print('Downloading images...')
  threadPool = ThreadPool(50)
  threadPool.starmap(download_image, zip(urls.values(), urls.keys()))
  threadPool.close()
  threadPool.join()
  print('Downloaded all images')

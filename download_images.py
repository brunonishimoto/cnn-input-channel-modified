from __future__ import print_function
import os
import csv
import numpy as np
import urllib3
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

def rescale_image(image):
  _, g, _ = image.split()
  g = g.resize((128, 128))
  g_arr = np.array(g)
  g = np.zeros((256, 256))
  g[0:128, 0:128] = g_arr

  final = np.array(image)
  final[:, :, 1] = g
  return Image.fromarray(final)

def download_image(url, filename, force=False):
  directory = '/'.join(filename.split('/')[:-1])

  modified_file    = filename.split('/')
  modified_file[2] = modified_file[2] + '_modified'

  rescaled_file    = filename.split('/')
  rescaled_file[2] = rescaled_file[2] + '_rescaled'

  modified_dir  = modified_file[:-1]
  modified_dir  = '/'.join(modified_dir)
  modified_file = '/'.join(modified_file)

  rescaled_dir  = rescaled_file[:-1]
  rescaled_dir  = '/'.join(rescaled_dir)
  rescaled_file = '/'.join(rescaled_file)

  if not os.path.exists(directory):
    os.makedirs(directory, exist_ok=True)
  if not os.path.exists(modified_dir):
    os.makedirs(modified_dir, exist_ok=True)
  if not os.path.exists(rescaled_dir):
    os.makedirs(rescaled_dir, exist_ok=True)

  if (force or not os.path.exists(filename) or not os.path.exists(modified_file)) and url != '':
    try:
      connection_pool = urllib3.PoolManager()
      resp = connection_pool.request('GET',url )

      img = Image.open(BytesIO(resp.data))
      img = img.resize((256, 256))
      img.save(filename)

      try:
        img_modified = modify_image(img)
        img_modified.save(modified_file)
      except:
        pass

      try:
        img_rescaled = rescale_image(img)
        img_rescaled.save(rescaled_file)
      except:
        pass

      resp.release_conn()
    except Exception as e:
      print(e)
      try:
        os.remove(filename)
        os.remove(modified_file)
      except:
        pass

data_root = './dataset'
csv_dir = os.path.join(data_root, 'csv_files')
for directory in os.listdir(csv_dir):
  if (directory == 'train'):
    print (directory)
    files = os.listdir(os.path.join(csv_dir, directory))
    files.sort()

    actual_dir  = os.path.join(data_root, directory)
    dog_dir     = os.path.join(actual_dir, 'dog')
    not_dog_dir = os.path.join(actual_dir, 'not_dog')

    if not os.path.exists(dog_dir):
      os.makedirs(dog_dir, exist_ok=True)
    if not os.path.exists(not_dog_dir):
      os.makedirs(not_dog_dir, exist_ok=True)

    # Getting all ids
    ids = {}
    with open(os.path.join(csv_dir, directory, files[0])) as image_labels:
      reader = csv.DictReader(image_labels)
      for row in reader:
        if (row['Confidence'] == '1'):
          if (row['LabelName'] == '/m/0bt9lr'):
            ids[row['ImageID']] = 1
          else:
            if (row['ImageID'] not in ids):
              ids[row['ImageID']] = 0
    print('Got all ids')
    dogs_len = len([x for x in ids.values() if x == 1])
    print(dogs_len)
    print(len([x for x in ids.values() if x == 0]))
    # Getting all urls
    urls = {}
    count_not_dogs = 0
    count_dogs = 0
    with open(os.path.join(csv_dir, directory, files[1])) as image_ids:
      reader = csv.DictReader(image_ids)
      for row in reader:
        if row['ImageID'] in ids:
          if ids[row['ImageID']] == 1:
            if (count_dogs < 30000):
              urls[os.path.join(dog_dir, row['Thumbnail300KURL'].split('/')[-1]).split('?')[0]] = row['Thumbnail300KURL']
              count_dogs += 1
          # elif ids[row['ImageID']] == 0:
          #   if(count_not_dogs < count_dogs and count_not_dogs < 30000):
          #     urls[os.path.join(not_dog_dir, row['Thumbnail300KURL'].split('/')[-1]).split('?')[0]] = row['Thumbnail300KURL']
          #     count_not_dogs += 1
      print('Got all urls')
      print(len(urls))

    # Downloading images
    print('Downloading images...')
    threadPool = ThreadPool(50)
    threadPool.starmap(download_image, zip(urls.values(), urls.keys()))
    threadPool.close()
    threadPool.join()
    print('Downloaded all images')

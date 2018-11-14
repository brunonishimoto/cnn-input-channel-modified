import urllib3
from PIL import Image
from io import BytesIO
import numpy as np

urllib3.disable_warnings()
# url = 'https://c5.staticflickr.com/3/2287/1721186329_152c3e729c_z.jpg'
url = "https://www.indezine.com/products/powerpoint/learn/color/images/rgb01.png"

connection_pool = urllib3.PoolManager()
resp = connection_pool.request('GET',url )

img = Image.open(BytesIO(resp.data))
img = img.resize((256, 256))
img.save('./test.png')
# print(img.getbands())
im_short = img.resize((512, 512))
# im_short.save('./test1.png')

r, g, b, a = img.split()
# r_tmp = r
# print(r.shape)
# r[:, :, 1] *= 0
# r[:, :, 2] *= 0
r = r.resize((128, 128))
r = np.array(r)
r_big = np.zeros((256, 256))
r_big[0:128, 0:128] = r
print(r_big.shape)
r_mod = Image.fromarray(r_big)
print(r.shape)
r_mod.save('r.png')
g.save('g.png')
b.save('b.png')
# g = np.array(img)
# g_tmp = g
# g[:, :, 1] = np.flip(g[:, :, 1], 0)
# g = Image.fromarray(g)
# g.save('g.png')
# b = np.array(img)
# b_tmp = b
# b[:, :, 0] *= 0
# b[:, :, 1] *= 0
# b[:, :, 2] = np.flip(b[:, :, 2], 0)
# b = Image.fromarray(b)
# b.save('b.png')
# g = g.transpose(Image.FLIP_LEFT_RIGHT)
# g.save('g1.png')
# b.save('b.png')
# final = r_tmp
# final[:, :, 1] = g_tmp[:, :, 1]
# final[:, :, 2] = b_tmp[:, :, 2]
# final = Image.fromarray(final)
# final.save('final.png')
resp.release_conn()
